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

// Video change monitoring
let lastProcessedVideoId = null;
let videoChangeCheckInterval = null;

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
  
  // Start monitoring for video changes (for auto-detection after scroll)
  startVideoChangeMonitor();
  
  // Process first video
  processCurrentVideo();
}

// Stop calibration
function stopCalibration() {
  isCalibrating = false;
  stats.status = 'Stopped';
  console.log('[ScrollMaxxr] Calibration stopped');
  
  // Stop video change monitor
  stopVideoChangeMonitor();
  
  // Clear saved state
  chrome.storage.local.remove(['isCalibrating', 'selectedCategory', 'categoryDescription', 'stats']);
}

// Get current video ID from DOM
function getCurrentVideoId() {
  try {
    const videos = Array.from(document.querySelectorAll('video'));
    let activeVideo = null;
    
    for (const vid of videos) {
      const rect = vid.getBoundingClientRect();
      const isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight * 1.5;
      const isPlaying = !vid.paused;
      
      if (isVisible || isPlaying) {
        activeVideo = vid;
        break;
      }
    }
    
    if (!activeVideo && videos.length > 0) {
      activeVideo = videos[0];
    }
    
    if (!activeVideo) return null;
    
    const container = activeVideo.closest('[data-e2e="recommend-list-item"]') || 
                     activeVideo.closest('div[class*="DivVideoContainer"]') ||
                     activeVideo.closest('div[class*="ItemContainer"]');
    
    if (container) {
      const link = container.querySelector('a[href*="/video/"]');
      if (link) {
        const match = link.href.match(/\/video\/(\d+)/);
        return match ? match[1] : null;
      }
    }
    
    const allLinks = Array.from(document.querySelectorAll('a[href*="/video/"]'));
    for (const link of allLinks) {
      const rect = link.getBoundingClientRect();
      if (rect.top >= 0 && rect.bottom <= window.innerHeight * 1.5) {
        const match = link.href.match(/\/video\/(\d+)/);
        if (match) return match[1];
      }
    }
    
    return null;
  } catch (error) {
    return null;
  }
}

// Start monitoring for video changes
function startVideoChangeMonitor() {
  console.log('[ScrollMaxxr] 🔄 Starting video change monitor');
  
  lastProcessedVideoId = getCurrentVideoId();
  console.log('[ScrollMaxxr] Initial video ID:', lastProcessedVideoId);
  
  videoChangeCheckInterval = setInterval(() => {
    if (!isCalibrating) {
      stopVideoChangeMonitor();
      return;
    }
    
    const currentVideoId = getCurrentVideoId();
    if (currentVideoId && currentVideoId !== lastProcessedVideoId) {
      console.log('[ScrollMaxxr] 🎉 New video detected! (', lastProcessedVideoId, '→', currentVideoId, ')');
      lastProcessedVideoId = currentVideoId;
      
      // Process the new video after a short delay
      setTimeout(processCurrentVideo, 1500);
    }
  }, 500);
}

// Stop video change monitor
function stopVideoChangeMonitor() {
  if (videoChangeCheckInterval) {
    clearInterval(videoChangeCheckInterval);
    videoChangeCheckInterval = null;
    console.log('[ScrollMaxxr] ⏹️ Stopped video change monitor');
  }
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

        // Determine match based on confidence threshold (>= 0.5)
        const CONFIDENCE_THRESHOLD = 0.5;
        const isMatch = response.confidence >= CONFIDENCE_THRESHOLD;

        // Update stats
        stats.videosProcessed++;
        if (isMatch) {
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
        if (isMatch) {
          console.log(`[ScrollMaxxr] Match found! (confidence ${response.confidence} >= ${CONFIDENCE_THRESHOLD}) Liking video...`);
          await likeVideo();
        } else {
          console.log(`[ScrollMaxxr] No match (confidence ${response.confidence} < ${CONFIDENCE_THRESHOLD}), scrolling...`);
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
    console.log('[ScrollMaxxr] 🔍 Debugging video data extraction...');
    
    // Find the CURRENTLY PLAYING video (not just any video in DOM)
    // TikTok loads multiple videos, so we need to find the visible one
    const videos = Array.from(document.querySelectorAll('video'));
    console.log('[ScrollMaxxr] Found', videos.length, 'video elements in DOM');
    
    // Find the video that's actually playing/visible
    let activeVideo = null;
    for (const vid of videos) {
      const rect = vid.getBoundingClientRect();
      const isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight * 1.5;
      const isPlaying = !vid.paused;
      
      if (isVisible || isPlaying) {
        activeVideo = vid;
        console.log('[ScrollMaxxr] Found active video:', {
          isVisible,
          isPlaying,
          top: rect.top,
          bottom: rect.bottom
        });
        break;
      }
    }
    
    if (!activeVideo && videos.length > 0) {
      // Fallback: use the first video
      activeVideo = videos[0];
      console.log('[ScrollMaxxr] Using first video as fallback');
    }
    
    if (!activeVideo) {
      console.log('[ScrollMaxxr] No video element found');
      return null;
    }
    
    // Find the container for this specific video
    const videoContainer = activeVideo.closest('[data-e2e="recommend-list-item"]') || 
                          activeVideo.closest('div[class*="DivVideoContainer"]') ||
                          activeVideo.closest('div[class*="ItemContainer"]');
    
    console.log('[ScrollMaxxr] Video container found:', !!videoContainer);

    // USERNAME DETECTION - Look within the active video's container first
    let username = '';
    let usernameEl = null;
    
    if (videoContainer) {
      // Method 1: Within container - browse username
      usernameEl = videoContainer.querySelector('[data-e2e="browse-username"]') ||
                   videoContainer.querySelector('[data-e2e="video-author-uniqueid"]') ||
                   videoContainer.querySelector('a[href^="/@"]');
      
      if (usernameEl) {
        if (usernameEl.tagName === 'A') {
          const match = usernameEl.href.match(/@([^/?]+)/);
          if (match) username = match[1];
        } else {
          username = usernameEl.textContent?.trim().replace('@', '') || '';
        }
        console.log('[ScrollMaxxr] Found username from active video container:', username);
      }
    }
    
    // Method 2: Fallback to global search
    if (!username) {
      usernameEl = document.querySelector('[data-e2e="browse-username"]') ||
                   document.querySelector('[data-e2e="video-author-uniqueid"]');
      if (usernameEl) {
        username = usernameEl.textContent?.trim().replace('@', '') || '';
        console.log('[ScrollMaxxr] Found username via global search:', username);
      }
    }
    
    // Method 3: Any profile link
    if (!username) {
      const profileLinks = Array.from(document.querySelectorAll('a[href*="/@"]'));
      if (profileLinks.length > 0) {
        const match = profileLinks[0].href.match(/@([^/?]+)/);
        if (match) {
          username = match[1];
          console.log('[ScrollMaxxr] Found username via profile link:', username);
        }
      }
    }
    
    if (!username) {
      console.error('[ScrollMaxxr] ❌ Could not find username!');
      return null;
    }
    
    // VIDEO ID DETECTION - Look within the active video's container
    let videoId = '';
    
    if (videoContainer) {
      // Method 1: From container's video link
      const containerLink = videoContainer.querySelector('a[href*="/video/"]');
      if (containerLink) {
        const match = containerLink.href.match(/\/video\/(\d+)/);
        if (match) {
          videoId = match[1];
          console.log('[ScrollMaxxr] Found video ID from active container:', videoId);
        }
      }
    }
    
    // Method 2: Current URL (if on a specific video page)
    if (!videoId) {
      const urlMatch = window.location.href.match(/\/video\/(\d+)/);
      if (urlMatch) {
        videoId = urlMatch[1];
        console.log('[ScrollMaxxr] Found video ID from URL:', videoId);
      }
    }
    
    // Method 3: Find closest visible video link
    if (!videoId) {
      const allVideoLinks = Array.from(document.querySelectorAll('a[href*="/video/"]'));
      for (const link of allVideoLinks) {
        const rect = link.getBoundingClientRect();
        if (rect.top >= 0 && rect.bottom <= window.innerHeight * 1.5) {
          const match = link.href.match(/\/video\/(\d+)/);
          if (match) {
            videoId = match[1];
            console.log('[ScrollMaxxr] Found video ID from visible link:', videoId);
            break;
          }
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

// Scroll to next video (video change monitor will detect the new video)
async function scrollToNextVideo() {
  try {
    console.log('[ScrollMaxxr] 📜 Scrolling to next video...');
    
    // Method 1: Arrow Down (most reliable for TikTok)
    document.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'ArrowDown',
      code: 'ArrowDown',
      keyCode: 40,
      which: 40,
      bubbles: true,
      cancelable: true
    }));
    
    // Small delay, then try wheel event as backup
    await sleep(500);
    
    // Method 2: Wheel event
    window.dispatchEvent(new WheelEvent('wheel', {
      deltaY: window.innerHeight,
      bubbles: true,
      cancelable: true
    }));
    
    // Method 3: Direct scroll as last resort
    await sleep(500);
    window.scrollBy({
      top: window.innerHeight,
      behavior: 'smooth'
    });
    
    console.log('[ScrollMaxxr] Scroll triggered, video change monitor will detect new video');
    // The video change monitor will automatically process the new video when detected
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
    
    // Resume calibration with video monitor
    console.log('[ScrollMaxxr] Resuming calibration for:', selectedCategory);
    startVideoChangeMonitor();
    setTimeout(processCurrentVideo, 2000); // Wait for page to load
  }
});

// Initialize
console.log('[ScrollMaxxr] Content script loaded on TikTok');

