# TikTok FYP Calibrator - MVP Requirements

**Last Updated:** November 9, 2025

---

## MVP Definition

**Minimum Viable Product for Go On Hacks 2025 Hackathon Demo:**

A working Chrome extension that automatically scrolls through TikTok, uses AI to classify videos into user-selected categories, likes matching content, and provides real-time progress updates—all demonstrable in a 3-5 minute live demo.

**Core Value Proposition:**
Automate 30 minutes of manual FYP curation in 2-3 minutes using AI.

**Demo Requirements:**
- Must work end-to-end on real TikTok
- Must visibly classify and act on 15+ videos
- Must show real-time stats updating
- Must complete successfully without crashes

**Out of Scope for MVP:**
- Next.js webapp (landing page/dashboard)
- User authentication
- Database persistence
- Multi-account support
- Advanced analytics
- Mobile app

---

## Core Features (Must-Have - Hours 0-18)

### Priority 1: Chrome Extension Core (Hours 0-6)

#### 1.1 Extension Manifest Setup
**Time: 30 minutes**

**File**: `extension/manifest.json`

**Requirements:**
- [ ] Use Manifest V3 (required for new Chrome extensions)
- [ ] Request permissions: `activeTab`, `storage`, `scripting`
- [ ] Define host permissions for `*://*.tiktok.com/*`
- [ ] Configure popup, content script, and background service worker
- [ ] Set up icons (16px, 48px, 128px)

**Implementation:**
```json
{
  "manifest_version": 3,
  "name": "ScrollMaxxr - FYP Calibrator",
  "version": "1.0.0",
  "description": "AI-powered TikTok FYP optimization",
  "permissions": ["activeTab", "storage", "scripting"],
  "host_permissions": ["*://*.tiktok.com/*"],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "assets/icons/icon16.png",
      "48": "assets/icons/icon48.png",
      "128": "assets/icons/icon128.png"
    }
  },
  "background": {
    "service_worker": "background/background.js"
  },
  "content_scripts": [
    {
      "matches": ["*://*.tiktok.com/*"],
      "js": ["content/content.js"],
      "run_at": "document_idle"
    }
  ]
}
```

**Testing:**
- [ ] Extension loads in Chrome without errors
- [ ] Popup opens when icon clicked
- [ ] Content script injects on TikTok pages

---

#### 1.2 Popup UI with Category Selection
**Time: 2-3 hours**

**Files**: 
- `extension/popup/popup.html`
- `extension/popup/popup.css`
- `extension/popup/popup.js`

**Requirements:**

**Visual Layout (320px × 480px):**
```
┌─────────────────────────────────┐
│  🎯 FYP Calibrator              │
│  Optimize your scroll           │
├─────────────────────────────────┤
│  Select Content Categories:     │
│                                 │
│  ☐ 🔥 Thirst Traps  ☐ 😂 Skits  │
│  ☐ 🧠 Brainrot      ☐ 💻 Tech   │
│  ☐ 📰 News          ☐ ✂️ Edits  │
│  ☐ 📸 Photography               │
│                                 │
│  ┌─────────────────────────┐   │
│  │  Start Calibration  ▶   │   │
│  └─────────────────────────┘   │
│                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━ 0%    │
│                                 │
│  📊 Videos Processed: 0         │
│  ✅ Matches Found: 0            │
│  📈 Match Rate: 0%              │
│  ⚡ Status: Ready               │
└─────────────────────────────────┘
```

**Functionality Checklist:**
- [ ] 7 category checkboxes (Thirst Traps, Skits, Brainrot, Tech, News, Edits, Photography)
- [ ] "Start Calibration" button (primary CTA)
- [ ] "Stop Calibration" button (hidden until active, red color)
- [ ] Progress bar (animated gradient, 0-100%)
- [ ] Real-time stats display:
  - Videos Processed counter
  - Matches Found counter
  - Match Rate percentage
  - Status text (Ready / Running / Complete / Error)
- [ ] Disable category checkboxes during calibration
- [ ] Save selected categories to Chrome Storage
- [ ] Load saved categories on popup open
- [ ] Error message display area
- [ ] Success celebration animation on completion

**HTML Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="popup.css">
  <title>FYP Calibrator</title>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <h1>🎯 FYP Calibrator</h1>
      <p class="tagline">Optimize your scroll</p>
    </div>

    <!-- Category Selection -->
    <div class="categories">
      <h3>Select Content Categories:</h3>
      <div class="category-grid">
        <label class="category-item">
          <input type="checkbox" id="thirst-traps" value="Thirst Traps">
          <span>🔥 Thirst Traps</span>
        </label>
        <label class="category-item">
          <input type="checkbox" id="skits" value="Skits">
          <span>😂 Skits</span>
        </label>
        <label class="category-item">
          <input type="checkbox" id="brainrot" value="Brainrot">
          <span>🧠 Brainrot</span>
        </label>
        <label class="category-item">
          <input type="checkbox" id="tech" value="Tech">
          <span>💻 Tech</span>
        </label>
        <label class="category-item">
          <input type="checkbox" id="news" value="News">
          <span>📰 News</span>
        </label>
        <label class="category-item">
          <input type="checkbox" id="edits" value="Edits">
          <span>✂️ Edits</span>
        </label>
        <label class="category-item">
          <input type="checkbox" id="photography" value="Photography">
          <span>📸 Photography</span>
        </label>
      </div>
    </div>

    <!-- Control Buttons -->
    <div class="controls">
      <button id="start-btn" class="btn btn-primary">
        Start Calibration ▶
      </button>
      <button id="stop-btn" class="btn btn-danger" style="display: none;">
        Stop ⏹
      </button>
    </div>

    <!-- Progress Section -->
    <div id="progress-section" style="display: none;">
      <div class="progress-bar">
        <div id="progress-fill" class="progress-fill" style="width: 0%"></div>
      </div>

      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">Videos Processed</div>
          <div class="stat-value" id="videos-processed">0</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Matches Found</div>
          <div class="stat-value" id="matches-found">0</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Match Rate</div>
          <div class="stat-value" id="match-rate">0%</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">Status</div>
          <div class="stat-value" id="status">Ready</div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div id="message" class="message"></div>

    <!-- Footer -->
    <div class="footer">
      <small>Made for Go On Hacks 2025</small>
    </div>
  </div>

  <script src="popup.js"></script>
</body>
</html>
```

**JavaScript Logic (popup.js):**
```javascript
// Get DOM elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const progressSection = document.getElementById('progress-section');
const messageDiv = document.getElementById('message');

// Category checkboxes
const categoryCheckboxes = document.querySelectorAll('.category-item input');

// Load saved categories
chrome.storage.local.get(['selectedCategories'], (result) => {
  if (result.selectedCategories) {
    result.selectedCategories.forEach(cat => {
      const checkbox = document.querySelector(`input[value="${cat}"]`);
      if (checkbox) checkbox.checked = true;
    });
  }
});

// Start calibration
startBtn.addEventListener('click', async () => {
  const selectedCategories = getSelectedCategories();
  
  if (selectedCategories.length === 0) {
    showMessage('Please select at least one category', 'error');
    return;
  }

  // Save categories
  await chrome.storage.local.set({ selectedCategories });

  // Update UI
  startBtn.style.display = 'none';
  stopBtn.style.display = 'block';
  progressSection.style.display = 'block';
  disableCategories(true);

  // Send message to content script
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, {
    action: 'start',
    categories: selectedCategories
  });

  showMessage('Calibration started...', 'success');
});

// Stop calibration
stopBtn.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, { action: 'stop' });
  
  resetUI();
  showMessage('Calibration stopped', 'info');
});

// Listen for stats updates
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'stats_update') {
    updateStats(message.data);
  } else if (message.type === 'calibration_complete') {
    onCalibrationComplete(message.data);
  } else if (message.type === 'error') {
    showMessage(message.message, 'error');
  }
});

// Helper functions
function getSelectedCategories() {
  return Array.from(categoryCheckboxes)
    .filter(cb => cb.checked)
    .map(cb => cb.value);
}

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
  showMessage(`✅ Calibration complete! Processed ${stats.videosProcessed} videos`, 'success');
  resetUI();
  // Add celebration animation
  document.body.classList.add('celebration');
  setTimeout(() => document.body.classList.remove('celebration'), 2000);
}

function resetUI() {
  startBtn.style.display = 'block';
  stopBtn.style.display = 'none';
  disableCategories(false);
}

function disableCategories(disabled) {
  categoryCheckboxes.forEach(cb => cb.disabled = disabled);
}

function showMessage(text, type) {
  messageDiv.textContent = text;
  messageDiv.className = `message message-${type}`;
  messageDiv.style.display = 'block';
  setTimeout(() => {
    messageDiv.style.display = 'none';
  }, 5000);
}
```

**Testing:**
- [ ] UI renders correctly (no layout issues)
- [ ] Checkboxes toggle properly
- [ ] Selected categories persist after closing popup
- [ ] Start button disabled until category selected
- [ ] Progress section shows/hides correctly
- [ ] Stats update in real-time when messages received

---

#### 1.3 Content Script (TikTok Interaction)
**Time: 2-3 hours**

**File**: `extension/content/content.js`

**Requirements:**
- [ ] Detect TikTok page load
- [ ] Identify video container element
- [ ] Set up observer for video changes
- [ ] Extract video metadata (caption, hashtags, username, URL)
- [ ] Capture screenshot of current video frame
- [ ] Send data to background worker for classification
- [ ] Execute actions based on classification (like/scroll)
- [ ] Handle errors gracefully
- [ ] Add human-like delays

**Implementation:**
```javascript
// State
let isCalibrating = false;
let selectedCategories = [];
let stats = {
  videosProcessed: 0,
  matchesFound: 0,
  matchRate: 0,
  status: 'Ready'
};

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'start') {
    startCalibration(message.categories);
  } else if (message.action === 'stop') {
    stopCalibration();
  }
});

// Start calibration
function startCalibration(categories) {
  isCalibrating = true;
  selectedCategories = categories;
  stats = { videosProcessed: 0, matchesFound: 0, matchRate: 0, status: 'Running' };
  
  console.log('🎯 Starting calibration with categories:', categories);
  
  // Start processing current video
  processCurrentVideo();
}

// Stop calibration
function stopCalibration() {
  isCalibrating = false;
  stats.status = 'Stopped';
  console.log('⏹ Calibration stopped');
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
      console.error('❌ Failed to extract video data');
      await scrollToNextVideo();
      return;
    }

    console.log('📹 Processing video:', videoData.videoUrl);

    // Send to background for classification
    chrome.runtime.sendMessage(
      { action: 'classify', data: videoData },
      async (response) => {
        if (response.error) {
          console.error('❌ Classification error:', response.error);
          await scrollToNextVideo();
          return;
        }

        console.log('🤖 Classification:', response);

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
          console.log('✅ Match! Liking video...');
          await likeVideo();
        } else {
          console.log('⏭️  No match, scrolling...');
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
    console.error('❌ Error processing video:', error);
    await scrollToNextVideo();
    setTimeout(processCurrentVideo, 1000);
  }
}

// Extract video data
async function extractVideoData() {
  try {
    // Caption
    const captionEl = document.querySelector('[data-e2e="browse-video-desc"]') ||
                      document.querySelector('[data-e2e="video-desc"]');
    const caption = captionEl?.textContent?.trim() || '';

    // Hashtags
    const hashtagEls = document.querySelectorAll('a[href*="/tag/"]');
    const hashtags = Array.from(hashtagEls).map(el => 
      el.textContent.replace('#', '').trim()
    );

    // Username
    const usernameEl = document.querySelector('[data-e2e="browse-username"]') ||
                       document.querySelector('[data-e2e="video-author-uniqueid"]');
    const username = usernameEl?.textContent?.trim().replace('@', '') || '';

    // Video URL
    const videoUrl = window.location.href;

    // Capture screenshot
    const screenshot = await captureScreenshot();

    return {
      caption,
      hashtags,
      username,
      videoUrl,
      screenshot,
      selectedCategories
    };
  } catch (error) {
    console.error('Error extracting video data:', error);
    return null;
  }
}

// Capture screenshot of current video
async function captureScreenshot() {
  try {
    const video = document.querySelector('video');
    if (!video) {
      throw new Error('No video element found');
    }

    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 720;
    canvas.height = video.videoHeight || 1280;

    // Draw video frame to canvas
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64 JPEG
    const screenshot = canvas.toDataURL('image/jpeg', 0.7);
    
    return screenshot;
  } catch (error) {
    console.error('Error capturing screenshot:', error);
    return null;
  }
}

// Like current video
async function likeVideo() {
  try {
    const likeButton = document.querySelector('[data-e2e="browse-like"]') ||
                       document.querySelector('[data-e2e="like-icon"]') ||
                       document.querySelector('button[aria-label*="like"]');
    
    if (likeButton) {
      // Check if already liked
      const isLiked = likeButton.querySelector('svg')?.classList.contains('active') ||
                      likeButton.getAttribute('aria-pressed') === 'true';
      
      if (!isLiked) {
        likeButton.click();
        console.log('❤️ Liked video');
        await sleep(randomDelay(500, 1000));
      } else {
        console.log('Already liked');
      }
    } else {
      console.warn('Like button not found');
    }
  } catch (error) {
    console.error('Error liking video:', error);
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

    // Wait for scroll and video load
    await sleep(randomDelay(1500, 2500));
  } catch (error) {
    console.error('Error scrolling:', error);
  }
}

// Check if calibration is complete
function isCalibrationComplete() {
  // Need at least 20 videos to calculate rolling average
  if (stats.videosProcessed < 20) return false;

  // Check if match rate is above threshold (70%)
  if (stats.matchRate >= 0.70) {
    console.log('🎉 Target match rate achieved!');
    return true;
  }

  // Max 100 videos (safety limit)
  if (stats.videosProcessed >= 100) {
    console.log('⚠️ Max videos reached');
    return true;
  }

  return false;
}

// Complete calibration
function completeCalibration() {
  isCalibrating = false;
  stats.status = 'Complete';

  console.log('✅ Calibration complete!', stats);

  // Send completion message
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
console.log('🎯 FYP Calibrator content script loaded');
```

**Testing:**
- [ ] Script loads on TikTok pages
- [ ] Can extract video metadata correctly
- [ ] Screenshots capture properly
- [ ] Like button clicks work
- [ ] Scrolling works smoothly
- [ ] Handles missing elements gracefully

---

#### 1.4 Background Service Worker
**Time: 1 hour**

**File**: `extension/background/background.js`

**Requirements:**
- [ ] Maintain connection to backend API
- [ ] Forward classification requests from content script to backend
- [ ] Establish WebSocket connection for real-time updates
- [ ] Handle API errors and retries
- [ ] Manage session state

**Implementation:**
```javascript
// Backend URL
const BACKEND_URL = 'http://localhost:8000';

// WebSocket connection
let ws = null;
let sessionId = null;

// Handle messages from content script and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'classify') {
    // Forward to backend
    classifyVideo(message.data)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true; // Async response
  }
});

// Classify video via backend API
async function classifyVideo(videoData) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/classify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(videoData)
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const result = await response.json();
    console.log('Classification result:', result);
    
    return result;
  } catch (error) {
    console.error('Error classifying video:', error);
    throw error;
  }
}

// Connect to WebSocket (optional for MVP)
function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  ws = new WebSocket(`${BACKEND_URL.replace('http', 'ws')}/ws/session`);

  ws.onopen = () => {
    console.log('✅ WebSocket connected');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 WebSocket message:', data);

    // Forward to popup
    chrome.runtime.sendMessage(data);
  };

  ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('🔌 WebSocket closed, reconnecting...');
    setTimeout(connectWebSocket, 5000);
  };
}

// Initialize
console.log('🎯 FYP Calibrator background worker loaded');
```

**Testing:**
- [ ] Can communicate with content script
- [ ] API requests work correctly
- [ ] Errors are handled gracefully
- [ ] WebSocket connects (optional)

---

### Priority 2: Backend API (Hours 0-6)

#### 2.1 FastAPI Project Setup
**Time: 30 minutes**

**Files**:
- `backend/main.py`
- `backend/requirements.txt`
- `backend/.env`

**Requirements:**
- [ ] Install FastAPI and dependencies
- [ ] Set up CORS middleware
- [ ] Create basic health check endpoint
- [ ] Load environment variables
- [ ] Configure Uvicorn server

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pillow==10.1.0
google-generativeai==0.3.1
openai==1.3.0
anthropic==0.7.0
websockets==12.0
python-dotenv==1.0.0
requests==2.31.0
pydantic==2.5.0
```

**main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="ScrollMaxxr Backend",
    description="TikTok FYP Calibrator API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ScrollMaxxr API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

**.env:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ENVIRONMENT=development
```

**Setup Commands:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

**Testing:**
- [ ] Server starts without errors
- [ ] `http://localhost:8000/` returns welcome message
- [ ] `http://localhost:8000/api/health` returns health status
- [ ] CORS allows requests from extension

---

#### 2.2 Classification Endpoint
**Time: 2 hours**

**File**: `backend/api/routes.py`

**Requirements:**
- [ ] Accept video data (caption, hashtags, screenshot, etc.)
- [ ] Validate input with Pydantic
- [ ] Call LLM classifier
- [ ] Return classification result
- [ ] Handle errors gracefully

**Implementation:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import base64
from PIL import Image
import io

router = APIRouter()

class VideoData(BaseModel):
    caption: str
    hashtags: List[str]
    username: str
    videoUrl: str
    screenshot: str  # base64 encoded
    selectedCategories: List[str]

class ClassificationResult(BaseModel):
    isMatch: bool
    category: str
    confidence: float
    reasoning: str = ""

@router.post("/api/classify", response_model=ClassificationResult)
async def classify_video(video_data: VideoData):
    """
    Classify a TikTok video using LLM.
    """
    try:
        # Decode screenshot
        if ',' in video_data.screenshot:
            image_data = video_data.screenshot.split(',')[1]
        else:
            image_data = video_data.screenshot
        
        image_bytes = base64.b64decode(image_data)
        
        # Import classifier (will implement in next section)
        from classifier.llm_classifier import LLMClassifier
        
        classifier = LLMClassifier()
        result = await classifier.classify(
            image=image_bytes,
            caption=video_data.caption,
            hashtags=video_data.hashtags,
            username=video_data.username,
            target_categories=video_data.selectedCategories
        )
        
        return result
        
    except Exception as e:
        print(f"Error classifying video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include router in main.py
# from api.routes import router
# app.include_router(router)
```

**Update main.py:**
```python
from api.routes import router
app.include_router(router)
```

**Testing:**
- [ ] Endpoint accepts POST requests
- [ ] Input validation works (rejects invalid data)
- [ ] Returns proper error messages
- [ ] Response matches expected schema

---

#### 2.3 WebSocket Endpoint (Optional for MVP)
**Time: 1 hour**

**File**: `backend/api/websocket.py`

**Requirements:**
- [ ] Accept WebSocket connections
- [ ] Handle session messages
- [ ] Broadcast stats updates
- [ ] Handle disconnections

**Implementation:**
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/session")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back for now
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**Testing:**
- [ ] WebSocket connections establish successfully
- [ ] Messages are received and broadcast
- [ ] Disconnections handled gracefully

---

### Priority 3: LLM Classification (Hours 7-10)

#### 3.1 Gemini Flash Integration
**Time: 2 hours**

**File**: `backend/classifier/llm_classifier.py`

**Requirements:**
- [ ] Set up Gemini API client
- [ ] Build classification prompt
- [ ] Send image + text to Gemini
- [ ] Parse JSON response
- [ ] Calculate confidence score
- [ ] Determine if match

**Implementation:**
```python
import google.generativeai as genai
import os
from PIL import Image
import io
import json
from typing import List

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

CATEGORIES = {
    "Thirst Traps": "Attractive people showing off, flirty content, dating advice, gym/fitness flexing",
    "Skits": "Comedy sketches, acting, roleplay, POV content, funny scenarios",
    "Brainrot": "Memes, chaotic edits, Gen Z humor, unhinged content, surreal humor",
    "Tech": "Programming, gadgets, software, AI, tutorials, tech reviews, coding",
    "News": "Current events, politics, world news, breaking news, journalism",
    "Edits": "AMVs, fan edits, transitions, video editing showcases, aesthetic videos",
    "Photography": "Photo tips, camera gear, composition, photo showcases, photography tutorials"
}

SYSTEM_PROMPT = """You are a TikTok content classifier. Analyze the video screenshot and metadata to determine which category it belongs to.

Categories:
{categories}

Return ONLY a JSON object in this exact format:
{{"category": "category_name", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}

Be strict in classification. If unsure, use confidence < 0.5.
"""

class LLMClassifier:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def classify(
        self,
        image: bytes,
        caption: str,
        hashtags: List[str],
        username: str,
        target_categories: List[str]
    ) -> dict:
        """
        Classify video content using Gemini.
        """
        try:
            # Build prompt
            categories_str = "\n".join([
                f"- {cat}: {CATEGORIES[cat]}"
                for cat in CATEGORIES.keys()
            ])
            
            system_prompt = SYSTEM_PROMPT.format(categories=categories_str)
            
            user_prompt = f"""
Caption: {caption}
Hashtags: {', '.join(hashtags)}
Username: @{username}

Analyze the image and text. Which category does this video belong to?
Return JSON only.
"""
            
            # Load image
            img = Image.open(io.BytesIO(image))
            
            # Generate classification
            response = self.model.generate_content([
                system_prompt,
                user_prompt,
                img
            ])
            
            # Parse response
            result_text = response.text.strip()
            
            # Extract JSON (handle markdown code blocks)
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            # Check if category is in target categories
            is_match = result['category'] in target_categories
            
            return {
                'isMatch': is_match,
                'category': result['category'],
                'confidence': result.get('confidence', 0.5),
                'reasoning': result.get('reasoning', '')
            }
            
        except Exception as e:
            print(f"Error in Gemini classification: {e}")
            # Fallback to rule-based
            return self._rule_based_classify(caption, hashtags, target_categories)
    
    def _rule_based_classify(self, caption: str, hashtags: List[str], target_categories: List[str]) -> dict:
        """
        Simple keyword-based classification as fallback.
        """
        text = (caption + ' ' + ' '.join(hashtags)).lower()
        
        # Keyword matching
        scores = {}
        for category, description in CATEGORIES.items():
            keywords = description.lower().split()
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # Get best match
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / 5, 1.0)
        
        is_match = best_category in target_categories
        
        return {
            'isMatch': is_match,
            'category': best_category,
            'confidence': confidence,
            'reasoning': 'Fallback rule-based classification'
        }
```

**Testing:**
- [ ] Gemini API connects successfully
- [ ] Classifications return valid JSON
- [ ] Confidence scores are reasonable (0-1)
- [ ] Fallback works when Gemini fails
- [ ] Target categories are respected

---

#### 3.2 GPT-4o-mini Fallback (Optional)
**Time: 30 minutes**

**File**: `backend/classifier/openai_classifier.py`

**Requirements:**
- [ ] Set up OpenAI client
- [ ] Similar prompt to Gemini
- [ ] Vision API for image analysis

**Implementation:**
```python
from openai import OpenAI
import base64

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def classify_with_openai(image: bytes, caption: str, hashtags: List[str], target_categories: List[str]) -> dict:
    """
    Classify using GPT-4o-mini as fallback.
    """
    try:
        # Encode image
        image_base64 = base64.b64encode(image).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT.format(categories="\n".join([f"- {k}: {v}" for k, v in CATEGORIES.items()]))
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Caption: {caption}\nHashtags: {', '.join(hashtags)}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        is_match = result['category'] in target_categories
        
        return {
            'isMatch': is_match,
            'category': result['category'],
            'confidence': result.get('confidence', 0.5),
            'reasoning': result.get('reasoning', '')
        }
    except Exception as e:
        print(f"OpenAI classification error: {e}")
        raise
```

**Testing:**
- [ ] OpenAI API works as fallback
- [ ] Results are similar to Gemini

---

### Priority 4: Automation Logic (Hours 11-14)

#### 4.1 Human-like Behavior
**Requirements:**
- [ ] Random delays between actions (1-3 seconds)
- [ ] Smooth scrolling
- [ ] Don't like already-liked videos
- [ ] Error recovery

**Already implemented in content.js above.**

#### 4.2 Progress Tracking
**Requirements:**
- [ ] Count videos processed
- [ ] Count matches found
- [ ] Calculate match rate
- [ ] Track recent matches for completion

**Already implemented in content.js above.**

#### 4.3 Completion Detection
**Requirements:**
- [ ] Check if match rate ≥70% over last 20 videos
- [ ] Max 100 videos safety limit
- [ ] Notify user on completion

**Already implemented in content.js above.**

---

### Priority 5: UI/UX Polish (Hours 15-18)

#### 5.1 Extension Popup Styling
**Time: 2 hours**

**File**: `extension/popup/popup.css`

**Requirements:**
- [ ] Dark mode by default
- [ ] Purple/pink gradient theme
- [ ] Smooth animations
- [ ] Responsive layout
- [ ] Beautiful progress bar

**Implementation:**
```css
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1a1a1a;
  --bg-tertiary: #2a2a2a;
  --accent-primary: #8b5cf6;
  --accent-secondary: #ec4899;
  --text-primary: #ffffff;
  --text-secondary: #a1a1aa;
  --success: #10b981;
  --error: #ef4444;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  width: 320px;
  min-height: 480px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.container {
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  font-weight: 800;
  margin-bottom: 4px;
}

.tagline {
  font-size: 14px;
  color: var(--text-secondary);
}

.categories h3 {
  font-size: 14px;
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.category-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 20px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-item:hover {
  background: var(--bg-tertiary);
  transform: scale(1.02);
}

.category-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.category-item input:checked + span {
  color: var(--accent-primary);
  font-weight: 600;
}

.controls {
  margin-bottom: 20px;
}

.btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
}

.btn-danger {
  background: var(--error);
  color: white;
  margin-top: 8px;
}

.progress-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  transition: width 0.5s ease;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stat-item {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-primary);
}

.message {
  padding: 12px;
  border-radius: 8px;
  margin: 12px 0;
  font-size: 14px;
}

.message-success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
  border: 1px solid var(--success);
}

.message-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error);
  border: 1px solid var(--error);
}

.footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 11px;
}

.celebration {
  animation: celebrate 0.5s ease;
}

@keyframes celebrate {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

**Testing:**
- [ ] Looks good in light and dark mode
- [ ] Animations are smooth
- [ ] Responsive to different popup sizes
- [ ] Colors match brand

---

#### 5.2 Loading States
**Requirements:**
- [ ] Spinner during classification
- [ ] Disabled buttons during processing
- [ ] Progress indicators

**Already implemented in popup.js above.**

#### 5.3 Error Handling
**Requirements:**
- [ ] User-friendly error messages
- [ ] Retry buttons
- [ ] Fallback behavior

**Already implemented in popup.js and content.js above.**

---

## Dependencies and Setup

### Backend Dependencies

Create `backend/requirements.txt`:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
google-generativeai==0.3.1
pillow==10.1.0
python-multipart==0.0.6
requests==2.31.0
openai==1.3.0
anthropic==0.7.0
python-dotenv==1.0.0
pydantic==2.5.0
```

### Environment Variables

Create `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
ENVIRONMENT=development
```

### Chrome Extension Structure

```
extension/
├── manifest.json
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
├── content/
│   └── content.js
├── background/
│   └── background.js
├── assets/
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
└── README.md
```

### Backend Structure

```
backend/
├── main.py
├── requirements.txt
├── .env
├── api/
│   ├── routes.py
│   └── websocket.py
├── classifier/
│   ├── llm_classifier.py
│   └── openai_classifier.py
├── models/
│   └── schemas.py
└── utils/
    └── helpers.py
```

---

## Testing Checklist

### Pre-Demo Testing

- [ ] Extension loads in Chrome without errors
- [ ] Popup UI renders correctly
- [ ] Backend API starts successfully
- [ ] Can access TikTok and detect videos
- [ ] Gemini API key works
- [ ] Screenshot capture works
- [ ] Classification returns results
- [ ] Like button clicks work
- [ ] Scrolling works smoothly
- [ ] Stats update in real-time
- [ ] Completion detection triggers
- [ ] Error messages display properly

### End-to-End Testing

- [ ] Full calibration run (20+ videos)
- [ ] Match rate calculation is accurate
- [ ] Completion triggers at 70% match rate
- [ ] Can stop mid-calibration
- [ ] Can restart after stopping
- [ ] Works on different TikTok accounts
- [ ] Works with different category combinations
- [ ] Handles network errors gracefully
- [ ] Handles TikTok UI changes

### Performance Testing

- [ ] Classification takes <2 seconds
- [ ] Total time for 50 videos: 2-4 minutes
- [ ] No memory leaks in extension
- [ ] Backend doesn't crash under load
- [ ] WebSocket stays connected

---

## Demo Requirements

### What MUST Work for Demo (Non-Negotiable)

1. **Live Extension Demonstration**
   - Show extension installed in Chrome
   - Open TikTok in browser
   - Show popup UI
   - Select categories (e.g., "Tech" and "Photography")
   - Click "Start Calibration"
   - Watch it work live for 2-3 minutes

2. **Real-time Stats Visible**
   - Videos Processed counter incrementing
   - Matches Found counter incrementing
   - Match Rate percentage updating
   - Progress bar filling

3. **Actual Actions Happening**
   - Hearts appearing on matched videos
   - Page scrolling automatically
   - Smooth, human-like behavior

4. **Completion**
   - Process completes successfully
   - Success message displays
   - Final stats shown

5. **Before/After Comparison**
   - Show old FYP (before calibration)
   - Show new FYP (after calibration)
   - Demonstrate improvement

### Backup Plan if Live Demo Fails

- [ ] Pre-recorded video of full calibration
- [ ] Screenshots of each step
- [ ] Slide deck explaining system
- [ ] Code walkthrough as fallback

---

## Phase 2 Features (Hours 19-24, Time Permitting)

### Next.js Webapp (Optional)

#### 6.1 Landing Page
**Time: 2 hours**

**File**: `webapp/app/page.tsx`

**Requirements:**
- [ ] Hero section with value prop
- [ ] Demo video embedded
- [ ] Feature list
- [ ] "Install Extension" CTA
- [ ] FAQ section

**Tech Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion

**Skip if:** Behind schedule on core MVP.

---

#### 6.2 Analytics Dashboard (Optional)
**Time: 3 hours**

**File**: `webapp/app/dashboard/page.tsx`

**Requirements:**
- [ ] Session history table
- [ ] Charts (match rate over time)
- [ ] Category distribution pie chart
- [ ] Time saved calculator

**Tech Stack:**
- Recharts
- shadcn/ui components
- TanStack Table

**Skip if:** Behind schedule on core MVP.

---

### Advanced Extension Features (Optional)

#### 6.3 Category Profiles
**Time: 1 hour**

**Requirements:**
- [ ] Save multiple category profiles
- [ ] Quick switch between profiles
- [ ] Naming profiles

**Skip if:** Behind schedule on core MVP.

---

#### 6.4 Scheduled Calibration
**Time: 2 hours**

**Requirements:**
- [ ] Set time for auto-calibration
- [ ] Chrome Alarms API
- [ ] Background calibration

**Skip if:** Behind schedule on core MVP.

---

## Risk Mitigation

### Potential Problems and Solutions

#### 1. TikTok Blocks Extension
**Risk:** High  
**Impact:** Critical

**Solutions:**
- Use random delays (1-3 seconds)
- Limit speed (max 20-30 videos/minute)
- Use real browser (not headless)
- Don't automate too aggressively
- Have backup demo video

---

#### 2. LLM is Slow
**Risk:** Medium  
**Impact:** High

**Solutions:**
- Use Gemini Flash (fastest model)
- Optimize image size (compress to 720p)
- Add loading indicators
- Show "Classifying..." message
- Consider caching common videos

---

#### 3. Classification Inaccurate
**Risk:** Medium  
**Impact:** Medium

**Solutions:**
- Add rule-based filters
- Improve prompts with few-shot examples
- Use confidence thresholds
- Allow manual corrections
- Combine multiple signals (image + text)

---

#### 4. WebSocket Connection Drops
**Risk:** Medium  
**Impact:** Low

**Solutions:**
- Auto-reconnect logic
- Fallback to polling
- Graceful degradation
- Buffer messages

---

#### 5. Can't Finish in Time
**Risk:** Medium  
**Impact:** Critical

**Solutions:**
- Focus on MVP only
- Skip Phase 2 features
- Use templates for UI
- Simplify to 4 categories instead of 7
- Skip WebSocket, use simple REST API

---

## Time Management

### Hour-by-Hour Breakdown

**Hours 0-2:** Setup
- Initialize extension structure
- Set up FastAPI backend
- Install dependencies
- Test basic connectivity

**Hours 3-6:** Core Extension
- Build popup UI
- Implement content script
- Test on TikTok

**Hours 7-10:** LLM Integration
- Set up Gemini API
- Build classifier
- Test classification

**Hours 11-14:** Automation
- Implement like/scroll logic
- Add completion detection
- Test end-to-end

**Hours 15-18:** Polish
- Style popup
- Add animations
- Error handling
- Final testing

**Hours 19-24:** Bonus (if time)
- Next.js landing page
- Dashboard
- Advanced features

---

## Success Criteria

### Must-Have (Demo Passes)
- [ ] Extension loads and works
- [ ] Classifies 20+ videos successfully
- [ ] Actions execute correctly
- [ ] Stats update in real-time
- [ ] Completes without crashing

### Nice-to-Have (Extra Points)
- [ ] Accuracy >75%
- [ ] Beautiful UI
- [ ] Landing page
- [ ] Dashboard with analytics

### Winning Criteria (Top 3)
- [ ] Flawless live demo
- [ ] Judges laugh/impressed
- [ ] "That's actually useful" reaction
- [ ] Technical depth appreciated
- [ ] Polish and UX shine

---

**Last Updated:** November 9, 2025

