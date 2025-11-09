/**
 * ScrollMaxxr Background Service Worker
 * Handles API communication with the backend
 */

// Backend URL (configurable)
const BACKEND_URL = 'http://localhost:8000';

// Session management
let activeSessionId = null;
let statsWebSocket = null;

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
    
  } else if (message.action === 'focusTab') {
    // Focus the TikTok tab so user can see calibration happening
    if (sender.tab) {
      chrome.tabs.update(sender.tab.id, { active: true });
      chrome.windows.update(sender.tab.windowId, { focused: true });
    }
    sendResponse({ success: true });
    
  } else if (message.action === 'startPlaywrightSession') {
    // Start new Playwright-based session
    startPlaywrightSession(message.data)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true;
    
  } else if (message.action === 'stopPlaywrightSession') {
    // Stop active Playwright session
    stopPlaywrightSession()
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true;
    
  } else if (message.action === 'getSessionStatus') {
    // Get current session status
    sendResponse({ 
      sessionId: activeSessionId, 
      isRunning: activeSessionId !== null 
    });
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
    
    // Get the tab to capture
    const tab = await chrome.tabs.get(tabId);
    
    // Capture the visible tab
    // Note: This requires <all_urls> permission to work continuously
    const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, {
      format: 'jpeg',
      quality: 60
    });

    console.log('[ScrollMaxxr BG] Screenshot captured successfully');
    return dataUrl;
  } catch (error) {
    console.error('[ScrollMaxxr BG] Screenshot capture failed:', error.message);
    
    // Check if it's a permission error
    if (error.message.includes('activeTab') || error.message.includes('permission')) {
      throw new Error('Screenshot permission denied. The extension needs <all_urls> permission to capture screenshots continuously. Please reload the extension and approve the permission request.');
    }
    
    throw error;
  }
}

// Start Playwright session
async function startPlaywrightSession({ category, categoryDescription }) {
  try {
    console.log('[ScrollMaxxr BG] Starting Playwright session...');
    
    // Get TikTok cookies
    const cookies = await chrome.cookies.getAll({ domain: '.tiktok.com' });
    console.log('[ScrollMaxxr BG] Extracted', cookies.length, 'cookies');
    
    // Convert to Playwright format
    const playwrightCookies = cookies.map(cookie => ({
      name: cookie.name,
      value: cookie.value,
      domain: cookie.domain,
      path: cookie.path,
      expires: cookie.expirationDate || -1,
      httpOnly: cookie.httpOnly || false,
      secure: cookie.secure || false,
      sameSite: cookie.sameSite || 'Lax'
    }));
    
    // Get user agent
    const userAgent = navigator.userAgent;
    
    // Start session on backend
    const response = await fetch(`${BACKEND_URL}/api/session/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        category,
        categoryDescription,
        cookies: playwrightCookies,
        userAgent
      })
    });
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to start session: ${error}`);
    }
    
    const result = await response.json();
    activeSessionId = result.session_id;
    
    console.log('[ScrollMaxxr BG] Session started:', activeSessionId);
    
    // Connect to WebSocket for live stats
    connectStatsWebSocket(activeSessionId);
    
    return {
      success: true,
      sessionId: activeSessionId,
      message: result.message
    };
    
  } catch (error) {
    console.error('[ScrollMaxxr BG] Failed to start session:', error);
    throw error;
  }
}

// Stop Playwright session
async function stopPlaywrightSession() {
  try {
    if (!activeSessionId) {
      return { success: true, message: 'No active session' };
    }
    
    console.log('[ScrollMaxxr BG] Stopping session:', activeSessionId);
    
    // Close WebSocket
    if (statsWebSocket) {
      statsWebSocket.close();
      statsWebSocket = null;
    }
    
    // Stop session on backend
    const response = await fetch(`${BACKEND_URL}/api/session/stop/${activeSessionId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to stop session: ${error}`);
    }
    
    const result = await response.json();
    activeSessionId = null;
    
    console.log('[ScrollMaxxr BG] Session stopped');
    
    return {
      success: true,
      message: result.message
    };
    
  } catch (error) {
    console.error('[ScrollMaxxr BG] Failed to stop session:', error);
    throw error;
  }
}

// Connect to WebSocket for live stats updates
function connectStatsWebSocket(sessionId) {
  try {
    const wsUrl = `ws://localhost:8000/api/session/ws/${sessionId}`;
    console.log('[ScrollMaxxr BG] Connecting to WebSocket:', wsUrl);
    
    statsWebSocket = new WebSocket(wsUrl);
    
    statsWebSocket.onopen = () => {
      console.log('[ScrollMaxxr BG] WebSocket connected');
    };
    
    statsWebSocket.onmessage = (event) => {
      try {
        const stats = JSON.parse(event.data);
        console.log('[ScrollMaxxr BG] Stats update:', stats);
        
        // Broadcast to popup if open
        chrome.runtime.sendMessage({
          type: 'stats_update',
          data: stats
        }).catch(() => {
          // Popup might be closed, ignore error
        });
      } catch (error) {
        console.error('[ScrollMaxxr BG] Error parsing stats:', error);
      }
    };
    
    statsWebSocket.onerror = (error) => {
      console.error('[ScrollMaxxr BG] WebSocket error:', error);
    };
    
    statsWebSocket.onclose = () => {
      console.log('[ScrollMaxxr BG] WebSocket closed');
      statsWebSocket = null;
    };
    
  } catch (error) {
    console.error('[ScrollMaxxr BG] Failed to connect WebSocket:', error);
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

