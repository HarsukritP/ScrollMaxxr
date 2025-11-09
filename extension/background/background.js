/**
 * ScrollMaxxr Background Service Worker
 * Handles API communication with the backend
 */

// Backend URL (configurable)
const BACKEND_URL = 'http://localhost:8000';

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'classify') {
    // Forward to backend for classification
    classifyVideo(message.data)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true; // Keep message channel open for async response
  } else if (message.action === 'captureScreenshot') {
    // Capture screenshot of the tab (bypasses CORS)
    captureTabScreenshot(sender.tab.id, message.cropData)
      .then(screenshot => sendResponse({ screenshot }))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Keep message channel open for async response
  }
});

// Classify video via backend API
async function classifyVideo(videoData) {
  try {
    console.log('[ScrollMaxxr BG] Classifying video...');
    console.log('[ScrollMaxxr BG] Video data:', {
      category: videoData.category,
      description: videoData.categoryDescription,
      caption: videoData.caption?.substring(0, 50) + '...',
      hashtags: videoData.hashtags,
      username: videoData.username,
      videoUrl: videoData.videoUrl,
      hasScreenshot: !!videoData.screenshot
    });
    
    const response = await fetch(`${BACKEND_URL}/api/classify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(videoData)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[ScrollMaxxr BG] API error response:', errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    console.log('[ScrollMaxxr BG] Classification result:', result);
    
    return result;
  } catch (error) {
    console.error('[ScrollMaxxr BG] Error classifying video:', error);
    
    // Check if backend is running
    if (error.message.includes('Failed to fetch')) {
      throw new Error('Backend not running. Please start the backend server at ' + BACKEND_URL);
    }
    
    throw error;
  }
}

// Capture screenshot using Chrome API (bypasses CORS)
async function captureTabScreenshot(tabId, cropData) {
  try {
    console.log('[ScrollMaxxr BG] Capturing screenshot of tab:', tabId);
    
    // Capture the visible tab (has permission to capture cross-origin content)
    const dataUrl = await chrome.tabs.captureVisibleTab(null, {
      format: 'jpeg',
      quality: 60
    });

    console.log('[ScrollMaxxr BG] Screenshot captured, processing...');

    // If crop data provided, crop to video area
    if (cropData && cropData.width > 0 && cropData.height > 0) {
      return await cropImage(dataUrl, cropData);
    }

    return dataUrl;
  } catch (error) {
    console.error('[ScrollMaxxr BG] Screenshot capture failed:', error);
    throw error;
  }
}

// Crop image to video bounds
async function cropImage(dataUrl, cropData) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      try {
        // Create canvas for cropping
        const canvas = new OffscreenCanvas(
          Math.min(cropData.width, 720),
          Math.min(cropData.height, 1280)
        );
        const ctx = canvas.getContext('2d');

        // Draw cropped region
        ctx.drawImage(
          img,
          cropData.x, cropData.y, cropData.width, cropData.height,  // Source
          0, 0, canvas.width, canvas.height  // Destination (scaled down if needed)
        );

        // Convert to base64 JPEG
        canvas.convertToBlob({ type: 'image/jpeg', quality: 0.6 })
          .then(blob => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
          })
          .catch(reject);
      } catch (error) {
        reject(error);
      }
    };
    img.onerror = reject;
    img.src = dataUrl;
  });
}

// Test backend connection on install
chrome.runtime.onInstalled.addListener(async () => {
  console.log('[ScrollMaxxr BG] Extension installed');
  
  // Test backend connection
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`);
    if (response.ok) {
      console.log('[ScrollMaxxr BG] Backend connection: OK');
    } else {
      console.warn('[ScrollMaxxr BG] Backend connection: Failed');
    }
  } catch (error) {
    console.warn('[ScrollMaxxr BG] Backend not reachable. Make sure to start it before using the extension.');
  }
});

// Log when service worker starts
console.log('[ScrollMaxxr BG] Background service worker loaded');

