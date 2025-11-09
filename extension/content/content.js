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
  
  // Start processing current video
  processCurrentVideo();
}

// Stop calibration
function stopCalibration() {
  isCalibrating = false;
  stats.status = 'Stopped';
  console.log('[ScrollMaxxr] Calibration stopped');
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

    // Username - REQUIRED to identify video
    const usernameEl = document.querySelector('[data-e2e="browse-username"]') ||
                       document.querySelector('[data-e2e="video-author-uniqueid"]') ||
                       document.querySelector('a[href^="/@"]');
    const username = usernameEl?.textContent?.trim().replace('@', '') || '';
    
    // Try to find video ID from various sources
    let videoId = '';
    
    // Method 1: Try to find from link in current view
    const videoLink = document.querySelector('a[href*="/video/"]');
    if (videoLink) {
      const match = videoLink.href.match(/\/video\/(\d+)/);
      if (match) videoId = match[1];
    }
    
    // Method 2: Try from video element data attributes
    if (!videoId && video.closest('[data-e2e="recommend-list-item"]')) {
      const container = video.closest('[data-e2e="recommend-list-item"]');
      const link = container?.querySelector('a[href*="/video/"]');
      if (link) {
        const match = link.href.match(/\/video\/(\d+)/);
        if (match) videoId = match[1];
      }
    }
    
    // Construct proper video URL if we have both username and videoId
    let videoUrl = window.location.href;
    if (username && videoId) {
      videoUrl = `https://www.tiktok.com/@${username}/video/${videoId}`;
    }
    
    // If we still don't have a proper video identifier, skip
    if (!username) {
      console.log('[ScrollMaxxr] Cannot identify video (no username found)');
      return null;
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
    // Smooth scroll down one viewport height
    window.scrollBy({
      top: window.innerHeight,
      behavior: 'smooth'
    });

    console.log('[ScrollMaxxr] Scrolled to next video');
    
    // Wait for scroll and video load
    await sleep(randomDelay(1500, 2500));
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

// Initialize
console.log('[ScrollMaxxr] Content script loaded on TikTok');

