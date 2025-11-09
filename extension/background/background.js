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

