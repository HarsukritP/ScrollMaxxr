/**
 * ScrollMaxxr Popup Script
 * Handles UI interactions and communication with content script
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

// Start calibration
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
    // Save custom description
    await chrome.storage.local.set({ customDescription: customDesc });
  }

  // Save category
  await chrome.storage.local.set({ selectedCategory: category });

  // Update UI
  startBtn.style.display = 'none';
  stopBtn.style.display = 'block';
  progressSection.style.display = 'block';
  disableCategories(true);
  
  // Add loading state to button
  stopBtn.classList.add('loading');
  setTimeout(() => stopBtn.classList.remove('loading'), 500);

  // Send message to content script
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Check if on TikTok
    if (!tab.url.includes('tiktok.com')) {
      showMessage('Please open TikTok.com first', 'error');
      resetUI();
      return;
    }
    
    // Check if on a valid TikTok video page (For You Page or profile video)
    const isOnFYP = tab.url.includes('tiktok.com/foryou');
    const isOnVideo = tab.url.includes('tiktok.com/@') && tab.url.includes('/video/');
    
    if (!isOnFYP && !isOnVideo) {
      showMessage('Please navigate to tiktok.com/foryou', 'error');
      resetUI();
      return;
    }
    
    chrome.tabs.sendMessage(tab.id, {
      action: 'start',
      category: category,
      categoryDescription: categoryDescription
    }, (response) => {
      if (chrome.runtime.lastError) {
        showMessage('Failed to connect to TikTok page. Please refresh and try again.', 'error');
        resetUI();
      } else {
        showMessage('Calibration started...', 'success');
      }
    });
  } catch (error) {
    console.error('Error starting calibration:', error);
    showMessage('Error: ' + error.message, 'error');
    resetUI();
  }
});

// Stop calibration
stopBtn.addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { action: 'stop' });
    
    showMessage('Calibration stopped', 'info');
    resetUI();
  } catch (error) {
    console.error('Error stopping calibration:', error);
    resetUI();
  }
});

// Listen for stats updates from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'stats_update') {
    updateStats(message.data);
  } else if (message.type === 'calibration_complete') {
    onCalibrationComplete(message.data);
  } else if (message.type === 'error') {
    showMessage(message.message, 'error');
  }
});

// Helper functions
function updateStats(stats) {
  document.getElementById('videos-processed').textContent = stats.videosProcessed;
  document.getElementById('matches-found').textContent = stats.matchesFound;
  document.getElementById('match-rate').textContent = `${Math.round(stats.matchRate * 100)}%`;
  document.getElementById('status').textContent = stats.status;
  
  // Update progress bar
  const progressFill = document.getElementById('progress-fill');
  progressFill.style.width = `${stats.matchRate * 100}%`;
}

function onCalibrationComplete(stats) {
  const timesSaved = Math.round((stats.videosProcessed * 1.5) / 60); // Rough estimate
  showMessage(
    `Calibration complete! Processed ${stats.videosProcessed} videos. Time saved: ~${timesSaved}min`, 
    'success'
  );
  resetUI();
  
  // Add celebration animation
  document.body.classList.add('celebration');
  setTimeout(() => document.body.classList.remove('celebration'), 600);
}

function resetUI() {
  startBtn.style.display = 'block';
  stopBtn.style.display = 'none';
  disableCategories(false);
}

function disableCategories(disabled) {
  categorySection.classList.toggle('disabled', disabled);
  categorySelect.disabled = disabled;
  customDescription.disabled = disabled;
}

function showMessage(text, type) {
  messageDiv.textContent = text;
  messageDiv.className = `message message-${type}`;
  messageDiv.style.display = 'block';
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    messageDiv.style.display = 'none';
  }, 5000);
}

// Check current page on popup open
async function checkPageStatus() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const pageStatus = document.getElementById('page-status');
    
    if (!tab.url.includes('tiktok.com')) {
      pageStatus.innerHTML = 'Not on TikTok - Please navigate to <strong>tiktok.com/foryou</strong>';
      pageStatus.className = 'page-status status-error';
      startBtn.disabled = true;
    } else if (tab.url.includes('/foryou')) {
      pageStatus.innerHTML = 'On For You Page - Ready to calibrate';
      pageStatus.className = 'page-status status-success';
      startBtn.disabled = false;
    } else if (tab.url.includes('/@') && tab.url.includes('/video/')) {
      pageStatus.innerHTML = 'On TikTok video - Ready to calibrate';
      pageStatus.className = 'page-status status-success';
      startBtn.disabled = false;
    } else {
      pageStatus.innerHTML = 'Please navigate to <strong>tiktok.com/foryou</strong> to start';
      pageStatus.className = 'page-status status-warning';
      startBtn.disabled = true;
    }
  } catch (error) {
    console.error('Error checking page status:', error);
  }
}

// Initialize
checkPageStatus();
console.log('ScrollMaxxr popup loaded');

