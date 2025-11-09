/**
 * ScrollMaxxr Content Script
 * Runs on TikTok pages - handles video detection, scrolling, and actions
 */

// State
let isCalibrating = false;
let selectedCategory = '';
let categoryDescription = '';
let stats = {
  videosProcessed: 0,
  matchesFound: 0,
  matchRate: 0,
  status: 'Ready'
};

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'start') {
    startCalibration(message.category, message.categoryDescription);
    sendResponse({ success: true });
  } else if (message.action === 'stop') {
    stopCalibration();
    sendResponse({ success: true });
  }
  return true; // Keep message channel open for async response
});

// Start calibration
function startCalibration(category, description) {
  isCalibrating = true;
  selectedCategory = category;
  categoryDescription = description;
  stats = { videosProcessed: 0, matchesFound: 0, matchRate: 0, status: 'Running' };
  
  console.log('[ScrollMaxxr] Starting calibration');
  console.log('[ScrollMaxxr] Category:', category);
  console.log('[ScrollMaxxr] Description:', description);
  
  // Save state to survive page navigation/refresh
  chrome.storage.local.set({
    isCalibrating: true,
    selectedCategory: category,
    categoryDescription: description,
    stats: stats
  });
  
  // Make TikTok tab active and focused (so user can see it working)
  chrome.runtime.sendMessage({ action: 'focusTab' });
  
  // Start processing current video
  processCurrentVideo();
}

// Stop calibration
function stopCalibration() {
  isCalibrating = false;
  stats.status = 'Stopped';
  console.log('[ScrollMaxxr] Calibration stopped');
  
  // Clear saved state
  chrome.storage.local.remove(['isCalibrating', 'selectedCategory', 'categoryDescription', 'stats']);
}

// Process current video
async function processCurrentVideo() {
  if (!isCalibrating) return;

  try {
    // Check if extension context is still valid
    if (!isExtensionContextValid()) {
      console.error('[ScrollMaxxr] Extension context invalidated - please reload the page');
      stopCalibration();
      alert('ScrollMaxxr extension was reloaded. Please refresh this page to continue.');
      return;
    }

    // Wait a bit for video to load
    await sleep(1000);

    // Extract video data
    const videoData = await extractVideoData();
    
    if (!videoData) {
      console.error('[ScrollMaxxr] Failed to extract video data');
      await scrollToNextVideo();
      setTimeout(processCurrentVideo, 1000);
      return;
    }

    console.log('[ScrollMaxxr] Processing video:', videoData.videoUrl);

    // Send to background for classification
    chrome.runtime.sendMessage(
      { action: 'classify', data: videoData },
      async (response) => {
        if (chrome.runtime.lastError) {
          const errorMsg = chrome.runtime.lastError.message;
          
          // Check for context invalidation
          if (errorMsg.includes('Extension context invalidated')) {
            console.error('[ScrollMaxxr] Extension context invalidated - stopping calibration');
            stopCalibration();
            alert('ScrollMaxxr extension was reloaded. Please refresh this page to continue.');
            return;
          }
          
          console.error('[ScrollMaxxr] Classification error:', errorMsg);
          await scrollToNextVideo();
          setTimeout(processCurrentVideo, 1000);
          return;
        }

        if (response.error) {
          console.error('[ScrollMaxxr] Classification error:', response.error);
          await scrollToNextVideo();
          setTimeout(processCurrentVideo, 1000);
          return;
        }

        console.log('[ScrollMaxxr] Classification:', response);

        // Update stats
        stats.videosProcessed++;
        if (response.isMatch) {
          stats.matchesFound++;
        }
        stats.matchRate = stats.matchesFound / stats.videosProcessed;

        // Send stats update to popup (with error handling)
        try {
          chrome.runtime.sendMessage({
            type: 'stats_update',
            data: stats
          });
        } catch (e) {
          // Ignore errors sending stats (extension may have been reloaded)
          console.warn('[ScrollMaxxr] Could not send stats update');
        }

        // Execute action
        if (response.isMatch) {
          console.log('[ScrollMaxxr] Match found! Liking video...');
          await likeVideo();
        } else {
          console.log('[ScrollMaxxr] No match, scrolling...');
        }

        await scrollToNextVideo();

        // Check completion
        if (isCalibrationComplete()) {
          completeCalibration();
        } else {
          // Process next video
          setTimeout(processCurrentVideo, 1000);
        }
      }
    );
  } catch (error) {
    console.error('[ScrollMaxxr] Error processing video:', error);
    
    // Check if it's a context invalidation error
    if (error.message && error.message.includes('Extension context invalidated')) {
      console.error('[ScrollMaxxr] Extension was reloaded - stopping');
      stopCalibration();
      alert('ScrollMaxxr extension was reloaded. Please refresh this page to continue.');
      return;
    }
    
    await scrollToNextVideo();
    setTimeout(processCurrentVideo, 1000);
  }
}

// Extract video data
async function extractVideoData() {
  try {
    // First, check if there's a video element
    const video = document.querySelector('video');
    if (!video) {
      console.log('[ScrollMaxxr] No video element found');
      return null;
    }

    console.log('[ScrollMaxxr] 🔍 Debugging video data extraction...');

    // USERNAME DETECTION - Try multiple methods
    let username = '';
    
    // Method 1: Browse username
    let usernameEl = document.querySelector('[data-e2e="browse-username"]');
    if (usernameEl) {
      username = usernameEl.textContent?.trim().replace('@', '') || '';
      console.log('[ScrollMaxxr] Found username via browse-username:', username);
    }
    
    // Method 2: Video author uniqueid
    if (!username) {
      usernameEl = document.querySelector('[data-e2e="video-author-uniqueid"]');
      if (usernameEl) {
        username = usernameEl.textContent?.trim().replace('@', '') || '';
        console.log('[ScrollMaxxr] Found username via video-author-uniqueid:', username);
      }
    }
    
    // Method 3: Any link starting with /@
    if (!username) {
      usernameEl = document.querySelector('a[href^="/@"]');
      if (usernameEl) {
        const match = usernameEl.href.match(/@([^/?]+)/);
        if (match) {
          username = match[1];
          console.log('[ScrollMaxxr] Found username via profile link:', username);
        }
      }
    }
    
    // Method 4: Look for ANY links with /@
    if (!username) {
      const allLinks = Array.from(document.querySelectorAll('a[href*="/@"]'));
      console.log('[ScrollMaxxr] Found', allLinks.length, 'links with /@');
      if (allLinks.length > 0) {
        const firstLink = allLinks[0];
        const match = firstLink.href.match(/@([^/?]+)/);
        if (match) {
          username = match[1];
          console.log('[ScrollMaxxr] Found username via any profile link:', username);
        }
      }
    }
    
    if (!username) {
      console.error('[ScrollMaxxr] ❌ Could not find username!');
      console.log('[ScrollMaxxr] Available elements:', {
        'data-e2e=browse-username': !!document.querySelector('[data-e2e="browse-username"]'),
        'data-e2e=video-author-uniqueid': !!document.querySelector('[data-e2e="video-author-uniqueid"]'),
        'links with /@': document.querySelectorAll('a[href*="/@"]').length
      });
      return null;
    }
    
    // VIDEO ID DETECTION - Try multiple methods
    let videoId = '';
    
    // Method 1: Current URL
    const urlMatch = window.location.href.match(/\/video\/(\d+)/);
    if (urlMatch) {
      videoId = urlMatch[1];
      console.log('[ScrollMaxxr] Found video ID from URL:', videoId);
    }
    
    // Method 2: Try to find from link in current view
    if (!videoId) {
      const videoLink = document.querySelector('a[href*="/video/"]');
      if (videoLink) {
        const match = videoLink.href.match(/\/video\/(\d+)/);
        if (match) {
          videoId = match[1];
          console.log('[ScrollMaxxr] Found video ID from video link:', videoId);
        }
      }
    }
    
    // Method 3: Try from video element's parent container
    if (!videoId && video.closest('[data-e2e="recommend-list-item"]')) {
      const container = video.closest('[data-e2e="recommend-list-item"]');
      const link = container?.querySelector('a[href*="/video/"]');
      if (link) {
        const match = link.href.match(/\/video\/(\d+)/);
        if (match) {
          videoId = match[1];
          console.log('[ScrollMaxxr] Found video ID from container:', videoId);
        }
      }
    }
    
    // Method 4: Look for ANY video links
    if (!videoId) {
      const allVideoLinks = Array.from(document.querySelectorAll('a[href*="/video/"]'));
      console.log('[ScrollMaxxr] Found', allVideoLinks.length, 'video links');
      if (allVideoLinks.length > 0) {
        const firstLink = allVideoLinks[0];
        const match = firstLink.href.match(/\/video\/(\d+)/);
        if (match) {
          videoId = match[1];
          console.log('[ScrollMaxxr] Found video ID from any video link:', videoId);
        }
      }
    }
    
    // Construct proper video URL
    let videoUrl = window.location.href;
    if (username && videoId) {
      videoUrl = `https://www.tiktok.com/@${username}/video/${videoId}`;
      console.log('[ScrollMaxxr] ✅ Constructed video URL:', videoUrl);
    } else {
      console.warn('[ScrollMaxxr] ⚠️ Using current URL as fallback:', videoUrl);
      console.log('[ScrollMaxxr] username:', username, 'videoId:', videoId);
    }

    // Caption
    const captionEl = document.querySelector('[data-e2e="browse-video-desc"]') ||
                      document.querySelector('[data-e2e="video-desc"]') ||
                      document.querySelector('[class*="DivItemContainer"] span[class*="SpanText"]');
    const caption = captionEl?.textContent?.trim() || '';

    // Hashtags
    const hashtagEls = document.querySelectorAll('a[href*="/tag/"]');
    const hashtags = Array.from(hashtagEls).map(el => 
      el.textContent.replace('#', '').trim()
    ).filter(Boolean);

    // Request screenshot from background script (has proper permissions)
    const screenshot = await requestScreenshot();
    
    if (!screenshot) {
      console.error('[ScrollMaxxr] Failed to capture screenshot');
      return null;
    }

    return {
      caption,
      hashtags,
      username,
      videoUrl,
      screenshot,
      category: selectedCategory,
      categoryDescription
    };
  } catch (error) {
    console.error('[ScrollMaxxr] Error extracting video data:', error);
    
    // Re-throw context invalidation errors so they're handled properly
    if (error.message && error.message.includes('Extension context invalidated')) {
      throw error;
    }
    
    return null;
  }
}

// Request screenshot from background script (bypasses CORS)
async function requestScreenshot() {
  try {
    // Check if extension context is still valid
    if (!isExtensionContextValid()) {
      throw new Error('Extension context invalidated');
    }

    // Get video element to determine crop area
    const video = document.querySelector('video');
    if (!video) {
      console.error('[ScrollMaxxr] No video element found');
      return null;
    }

    // Wait for video to load
    if (video.readyState < 2) {
      console.log('[ScrollMaxxr] Waiting for video to load...');
      await sleep(1000);
    }

    // Get video position and dimensions for cropping
    const rect = video.getBoundingClientRect();
    const cropData = {
      x: Math.round(rect.left),
      y: Math.round(rect.top),
      width: Math.round(rect.width),
      height: Math.round(rect.height)
    };

    console.log('[ScrollMaxxr] Requesting screenshot from background script...');

    // Request screenshot from background script
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: 'captureScreenshot', cropData },
        (response) => {
          if (chrome.runtime.lastError) {
            const errorMsg = chrome.runtime.lastError.message;
            console.error('[ScrollMaxxr] Screenshot request failed:', errorMsg);
            
            // Reject with the error (will be caught by extractVideoData)
            reject(new Error(errorMsg));
            return;
          }

          if (response && response.screenshot) {
            console.log('[ScrollMaxxr] Screenshot received:', response.screenshot.length, 'bytes');
            resolve(response.screenshot);
          } else {
            console.error('[ScrollMaxxr] No screenshot in response');
            reject(new Error('No screenshot data'));
          }
        }
      );
    });
  } catch (error) {
    console.error('[ScrollMaxxr] Screenshot request error:', error);
    throw error; // Re-throw to be caught by extractVideoData
  }
}

// Like current video
async function likeVideo() {
  try {
    const likeButton = document.querySelector('[data-e2e="browse-like"]') ||
                       document.querySelector('[data-e2e="like-icon"]') ||
                       document.querySelector('button[aria-label*="like"]') ||
                       document.querySelector('[class*="LikeButton"]');
    
    if (likeButton) {
      // Check if already liked
      const isLiked = likeButton.classList.contains('liked') ||
                      likeButton.getAttribute('aria-pressed') === 'true' ||
                      likeButton.querySelector('[fill="currentColor"]') !== null;
      
      if (!isLiked) {
        likeButton.click();
        console.log('[ScrollMaxxr] Video liked');
        await sleep(randomDelay(500, 1000));
      } else {
        console.log('[ScrollMaxxr] Video already liked');
      }
    } else {
      console.warn('[ScrollMaxxr] Like button not found');
    }
  } catch (error) {
    console.error('[ScrollMaxxr] Error liking video:', error);
  }
}

// Scroll to next video
async function scrollToNextVideo() {
  try {
    console.log('[ScrollMaxxr] Attempting to scroll to next video...');
    
    // Get current video URL to verify we actually moved
    const currentUrl = window.location.href;
    
    // Method 1: Click the down navigation button (most reliable)
    const downButton = document.querySelector('[data-e2e="arrow-down"]') ||
                      document.querySelector('button[aria-label*="Down"]') ||
                      document.querySelector('[class*="arrow-bottom"]');
    
    if (downButton && downButton.offsetParent !== null) {
      console.log('[ScrollMaxxr] Clicking down arrow button');
      downButton.click();
      await sleep(randomDelay(2000, 3000));
      
      // Verify we moved
      if (window.location.href !== currentUrl) {
        console.log('[ScrollMaxxr] ✅ Successfully navigated to next video');
        return;
      }
    }
    
    // Method 2: Arrow Down keypress
    console.log('[ScrollMaxxr] Trying Arrow Down key...');
    window.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'ArrowDown',
      code: 'ArrowDown',
      keyCode: 40,
      which: 40,
      bubbles: true,
      cancelable: true
    }));
    
    await sleep(randomDelay(2000, 3000));
    
    // Verify we moved
    if (window.location.href !== currentUrl) {
      console.log('[ScrollMaxxr] ✅ Arrow Down worked - navigated to next video');
      return;
    }
    
    // Method 3: Aggressive scroll
    console.log('[ScrollMaxxr] Trying aggressive scroll...');
    const scrollAmount = window.innerHeight * 1.2;
    window.scrollTo({
      top: window.scrollY + scrollAmount,
      behavior: 'smooth'
    });
    
    await sleep(randomDelay(2000, 3000));
    
    // Log result
    if (window.location.href !== currentUrl) {
      console.log('[ScrollMaxxr] ✅ Scroll worked - navigated to next video');
    } else {
      console.warn('[ScrollMaxxr] ⚠️ All scroll methods failed - URL unchanged');
      console.log('[ScrollMaxxr] Current URL:', currentUrl);
    }
  } catch (error) {
    console.error('[ScrollMaxxr] Error scrolling:', error);
  }
}

// Check if calibration is complete
function isCalibrationComplete() {
  // Need at least 20 videos to calculate meaningful rate
  if (stats.videosProcessed < 20) return false;

  // Check if match rate is above threshold (70%)
  if (stats.matchRate >= 0.70) {
    console.log('[ScrollMaxxr] Target match rate achieved!');
    return true;
  }

  // Max 100 videos (safety limit)
  if (stats.videosProcessed >= 100) {
    console.log('[ScrollMaxxr] Max videos reached');
    return true;
  }

  return false;
}

// Complete calibration
function completeCalibration() {
  isCalibrating = false;
  stats.status = 'Complete';

  console.log('[ScrollMaxxr] Calibration complete!', stats);

  // Send completion message to popup
  chrome.runtime.sendMessage({
    type: 'calibration_complete',
    data: stats
  });
}

// Utility functions
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function randomDelay(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function isExtensionContextValid() {
  try {
    // Try to access chrome.runtime.id - will throw if context is invalid
    return !!chrome.runtime?.id;
  } catch (e) {
    return false;
  }
}

// Restore state on page load (in case of tab switch/navigation)
chrome.storage.local.get(['isCalibrating', 'selectedCategory', 'categoryDescription', 'stats'], (result) => {
  if (result.isCalibrating) {
    console.log('[ScrollMaxxr] Restoring calibration state...');
    isCalibrating = result.isCalibrating;
    selectedCategory = result.selectedCategory;
    categoryDescription = result.categoryDescription;
    stats = result.stats || { videosProcessed: 0, matchesFound: 0, matchRate: 0, status: 'Running' };
    
    // Resume calibration
    console.log('[ScrollMaxxr] Resuming calibration for:', selectedCategory);
    setTimeout(processCurrentVideo, 2000); // Wait for page to load
  }
});

// Initialize
console.log('[ScrollMaxxr] Content script loaded on TikTok');

