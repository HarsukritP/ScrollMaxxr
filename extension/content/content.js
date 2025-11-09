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
        if (chrome.runtime.lastError || response.error) {
          console.error('[ScrollMaxxr] Classification error:', response?.error || chrome.runtime.lastError);
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

        // Send stats update to popup
        chrome.runtime.sendMessage({
          type: 'stats_update',
          data: stats
        });

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
    await scrollToNextVideo();
    setTimeout(processCurrentVideo, 1000);
  }
}

// Extract video data
async function extractVideoData() {
  try {
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

    // Username
    const usernameEl = document.querySelector('[data-e2e="browse-username"]') ||
                       document.querySelector('[data-e2e="video-author-uniqueid"]') ||
                       document.querySelector('a[href^="/@"]');
    const username = usernameEl?.textContent?.trim().replace('@', '') || 'unknown';

    // Video URL
    const videoUrl = window.location.href;

    // Capture screenshot
    const screenshot = await captureScreenshot();
    
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

// Capture screenshot of current video
async function captureScreenshot() {
  try {
    const video = document.querySelector('video');
    if (!video) {
      console.error('[ScrollMaxxr] No video element found');
      return null;
    }

    // Wait for video to have loaded frames
    if (video.readyState < 2) {
      console.log('[ScrollMaxxr] Waiting for video to load...');
      await sleep(1000);
    }

    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = Math.min(video.videoWidth || 720, 720);
    canvas.height = Math.min(video.videoHeight || 1280, 1280);

    // Draw video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64 JPEG (lower quality for faster upload)
    const screenshot = canvas.toDataURL('image/jpeg', 0.6);
    
    console.log('[ScrollMaxxr] Screenshot captured:', screenshot.length, 'bytes');
    return screenshot;
  } catch (error) {
    console.error('[ScrollMaxxr] Error capturing screenshot:', error);
    return null;
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

// Initialize
console.log('[ScrollMaxxr] Content script loaded on TikTok');

