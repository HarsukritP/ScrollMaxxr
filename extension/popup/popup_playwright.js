/**
 * ScrollMaxxr Popup Script (Playwright Mode)
 * Control panel for Playwright-based calibration sessions
 */

// DOM Elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const progressSection = document.getElementById('progress-section');
const messageDiv = document.getElementById('message');
const categorySelect = document.getElementById('category-select');
const customSection = document.getElementById('custom-section');
const customDescription = document.getElementById('custom-description');
const charCount = document.getElementById('char-count');
const categorySection = document.getElementById('category-section');

// Stats elements
const videosProcessedEl = document.getElementById('videos-processed');
const matchesFoundEl = document.getElementById('matches-found');
const matchRateEl = document.getElementById('match-rate');
const statusEl = document.getElementById('status');
const currentVideoEl = document.getElementById('current-video');

// State
let isRunning = false;
let sessionId = null;

// Show/hide custom description based on selection
categorySelect.addEventListener('change', () => {
  if (categorySelect.value === 'Custom') {
    customSection.style.display = 'block';
  } else {
    customSection.style.display = 'none';
  }
});

// Character counter for custom description
customDescription.addEventListener('input', () => {
  const length = customDescription.value.length;
  charCount.textContent = length;
  
  // Change color based on length
  if (length >= 10) {
    charCount.style.color = 'var(--success)';
  } else {
    charCount.style.color = 'var(--text-tertiary)';
  }
});

// Load saved category and description
chrome.storage.local.get(['selectedCategory', 'customDescription'], (result) => {
  if (result.selectedCategory) {
    categorySelect.value = result.selectedCategory;
    
    if (result.selectedCategory === 'Custom' && result.customDescription) {
      customSection.style.display = 'block';
      customDescription.value = result.customDescription;
      charCount.textContent = result.customDescription.length;
    }
  }
});

// Check if session is already running
checkSessionStatus();

// Start Playwright session
startBtn.addEventListener('click', async () => {
  const category = categorySelect.value;
  
  // Validation
  if (!category) {
    showMessage('Please select a category', 'error');
    return;
  }

  let categoryDescription = category;
  
  // If custom, validate description
  if (category === 'Custom') {
    const customDesc = customDescription.value.trim();
    if (!customDesc) {
      showMessage('Please describe your desired content', 'error');
      return;
    }
    if (customDesc.length < 10) {
      showMessage('Description must be at least 10 characters', 'error');
      return;
    }
    categoryDescription = customDesc;
    await chrome.storage.local.set({ customDescription: customDesc });
  }

  // Save category
  await chrome.storage.local.set({ selectedCategory: category });

  // Check if user is logged into TikTok (just need cookies, don't need tab open)
  showMessage('🔍 Checking TikTok login...', 'info');
  
  try {
    const cookies = await chrome.cookies.getAll({ domain: '.tiktok.com' });
    
    if (cookies.length === 0) {
      showMessage('⚠️ Please login to TikTok first (just visit tiktok.com and login)', 'error');
      return;
    }
    
    console.log('[Popup] Found', cookies.length, 'TikTok cookies');
    
    // Start Playwright session via background script
    showMessage('🚀 Starting headless browser...', 'info');
    startBtn.disabled = true;
    
    const response = await chrome.runtime.sendMessage({
      action: 'startPlaywrightSession',
      data: {
        category,
        categoryDescription
      }
    });
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    sessionId = response.sessionId;
    isRunning = true;
    
    // Update UI
    showUI('running');
    showMessage('✅ Running in background! You can close TikTok now.', 'success');
    statusEl.textContent = 'Running ⚡';
    
    console.log('[Popup] Session started:', sessionId);
    
  } catch (error) {
    console.error('[Popup] Failed to start session:', error);
    showMessage(`❌ Failed to start: ${error.message}`, 'error');
    startBtn.disabled = false;
  }
});

// Stop Playwright session
stopBtn.addEventListener('click', async () => {
  try {
    showMessage('⏹️ Stopping session...', 'info');
    stopBtn.disabled = true;
    
    const response = await chrome.runtime.sendMessage({
      action: 'stopPlaywrightSession'
    });
    
    if (response.error) {
      throw new Error(response.error);
    }
    
    isRunning = false;
    sessionId = null;
    
    // Update UI
    showUI('idle');
    showMessage('✅ Session stopped', 'success');
    statusEl.textContent = 'Stopped';
    
    console.log('[Popup] Session stopped');
    
  } catch (error) {
    console.error('[Popup] Failed to stop session:', error);
    showMessage(`❌ Failed to stop: ${error.message}`, 'error');
  } finally {
    stopBtn.disabled = false;
  }
});

// Listen for stats updates from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'stats_update') {
    updateStats(message.data);
  }
});

// Update stats display
function updateStats(stats) {
  console.log('[Popup] Stats update:', stats);
  
  videosProcessedEl.textContent = stats.stats?.videosProcessed || stats.videosProcessed || 0;
  matchesFoundEl.textContent = stats.stats?.matchesFound || stats.matchesFound || 0;
  
  const matchRate = stats.stats?.matchRate || stats.matchRate || 0;
  matchRateEl.textContent = Math.round(matchRate * 100) + '%';
  
  // Update status
  const status = stats.stats?.status || stats.status || 'idle';
  statusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1) + ' ⚡';
  
  // Update current video
  if (stats.stats?.currentVideo || stats.currentVideo) {
    const videoUrl = stats.stats?.currentVideo || stats.currentVideo;
    currentVideoEl.textContent = videoUrl.replace('https://www.tiktok.com/', '');
    currentVideoEl.title = videoUrl;
  }
  
  // Show last classification if available
  if (stats.lastClassification) {
    const { confidence, reasoning, isMatch } = stats.lastClassification;
    // Determine match based on confidence threshold (>= 0.5)
    const matchStatus = isMatch !== undefined ? isMatch : (confidence >= 0.5);
    const emoji = matchStatus ? '✅' : '❌';
    const confPercent = Math.round(confidence * 100);
    showMessage(`${emoji} ${matchStatus ? 'MATCH' : 'Skip'} (${confPercent}%): ${reasoning}`, 
                matchStatus ? 'success' : 'info');
  }
}

// Check session status on popup open
async function checkSessionStatus() {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'getSessionStatus'
    });
    
    if (response.isRunning && response.sessionId) {
      isRunning = true;
      sessionId = response.sessionId;
      showUI('running');
      statusEl.textContent = 'Running ⚡';
      console.log('[Popup] Resumed session:', sessionId);
    }
  } catch (error) {
    console.log('[Popup] No active session');
  }
}

// Show different UI states
function showUI(state) {
  if (state === 'running') {
    startBtn.style.display = 'none';
    stopBtn.style.display = 'block';
    progressSection.style.display = 'block';
    categorySection.style.pointerEvents = 'none';
    categorySection.style.opacity = '0.5';
  } else {
    startBtn.style.display = 'block';
    startBtn.disabled = false;
    stopBtn.style.display = 'none';
    progressSection.style.display = 'none';
    categorySection.style.pointerEvents = 'auto';
    categorySection.style.opacity = '1';
  }
}

// Show message
function showMessage(text, type = 'info') {
  messageDiv.textContent = text;
  messageDiv.className = 'message';
  
  if (type === 'error') {
    messageDiv.classList.add('error');
  } else if (type === 'success') {
    messageDiv.classList.add('success');
  }
  
  messageDiv.style.display = 'block';
}

// Initialize
console.log('[Popup] Playwright control panel loaded');

