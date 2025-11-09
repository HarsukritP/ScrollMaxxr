# TikTok FYP Calibrator - Project Scope

**Last Updated:** November 9, 2025

---

## Project Overview

### Project Name
**ScrollMaxxr** (TikTok FYP Calibrator)

### Tagline
*"Stop scrolling past content you hate. Let AI train your FYP in 2 minutes."*

### Elevator Pitch
Tired of your TikTok For You Page showing you content you don't care about? ScrollMaxxr is a Chrome extension powered by AI that automatically calibrates your FYP by intelligently liking videos you want and scrolling past ones you don't. Simply select your preferred content categories (Tech, Photography, News, etc.), hit start, and watch as our AI agent scrolls through TikTok, classifies content in real-time using multimodal LLMs, and trains your algorithm—all while you grab coffee. In 2-3 minutes, your FYP transforms from random chaos to perfectly curated content.

### Problem Statement

**The Problem:**
TikTok's algorithm is powerful but frustrating to train. To get the FYP you want, you need to:
- Manually scroll through hundreds of videos
- Like content you want more of
- Skip content you don't want (but the damage is done—you watched it)
- Spend 30+ minutes actively curating your feed
- Do this regularly as the algorithm drifts

This is tedious, time-consuming, and most people don't have the patience to do it properly.

**The Solution:**
ScrollMaxxr automates the entire calibration process using AI. It acts as your personal content curator, understanding your preferences and training your FYP automatically. What takes you 30 minutes of mind-numbing scrolling takes our AI agent 2-3 minutes of intelligent automation.

### Target Users

**Primary Users:**
- **Content Creators**: Want their FYP to show competitor content and trends in their niche
- **Niche Enthusiasts**: People with specific interests (tech, photography, finance) drowning in generic content
- **Privacy-Conscious Users**: Want to curate their feed without TikTok learning their actual viewing habits
- **Productivity Hackers**: Want an optimized FYP for learning/news without the rabbit hole

**Use Cases:**
1. **The Creator**: "I want only photography content so I can study composition techniques"
2. **The News Junkie**: "Show me news and tech, hide the thirst traps and brainrot"
3. **The Reset**: "My FYP is ruined, I need to start fresh"
4. **The Multi-Account Manager**: "I have separate accounts for work/personal and need different FYPs"

### Unique Value Proposition (Go On Hacks Edition)

**Why This is Perfect for Go On Hacks:**

1. **Weird but Practical**: It's a legitimate productivity tool disguised as a social media hack. You're essentially reverse-engineering TikTok's algorithm using AI to fight AI.

2. **Technically Impressive**: 
   - Multimodal LLM integration (analyzing both video frames and text)
   - Real-time classification and decision-making
   - Chrome extension communicating with backend via WebSockets
   - Anti-detection techniques to avoid TikTok's bot protection
   - Distributed system architecture in a hackathon timeframe

3. **Immediately Demonstrable**: Unlike most AI projects, this creates a visible, tangible result judges can see in real-time. We can literally show a before/after FYP transformation during the demo.

4. **Solves a Real Annoyance**: Everyone uses TikTok, everyone complains about their FYP. This is relatable and useful.

5. **Ethical Gray Area**: It's not malicious, but it's definitely bending the rules—the perfect hackathon vibe.

---

## Technical Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User's Browser                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Chrome Extension                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │ │
│  │  │  Popup   │  │ Content  │  │  Background Service  │ │ │
│  │  │    UI    │  │  Script  │  │       Worker         │ │ │
│  │  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘ │ │
│  │       │             │                    │             │ │
│  │       └─────────────┴────────────────────┘             │ │
│  └────────────────────────────┬────────────────────────────┘ │
└────────────────────────────────┼────────────────────────────┘
                                 │ WebSocket + REST API
                                 │
                    ┌────────────▼────────────┐
                    │   FastAPI Backend       │
                    │  ┌──────────────────┐   │
                    │  │  REST Endpoints  │   │
                    │  │  /api/classify   │   │
                    │  │  /api/session    │   │
                    │  └────────┬─────────┘   │
                    │  ┌────────▼─────────┐   │
                    │  │ WebSocket Server │   │
                    │  │  /ws/session     │   │
                    │  └────────┬─────────┘   │
                    │  ┌────────▼─────────┐   │
                    │  │ Session Manager  │   │
                    │  │ (State + Stats)  │   │
                    │  └────────┬─────────┘   │
                    └───────────┼─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   LLM Classification    │
                    │  ┌──────────────────┐   │
                    │  │ Gemini Flash 1.5 │   │
                    │  │   (Primary)      │   │
                    │  └────────┬─────────┘   │
                    │  ┌────────▼─────────┐   │
                    │  │  GPT-4o-mini     │   │
                    │  │   (Fallback)     │   │
                    │  └────────┬─────────┘   │
                    │  ┌────────▼─────────┐   │
                    │  │  Claude Haiku    │   │
                    │  │  (Fallback 2)    │   │
                    │  └──────────────────┘   │
                    └─────────────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │     Data Layer          │
                    │  ┌──────────────────┐   │
                    │  │  SQLite (MVP)    │   │
                    │  │  PostgreSQL      │   │
                    │  │  (Production)    │   │
                    │  └──────────────────┘   │
                    └─────────────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Next.js Webapp (Phase 2)│
                    │  ┌──────────────────┐   │
                    │  │  Landing Page    │   │
                    │  │  Dashboard       │   │
                    │  │  Analytics       │   │
                    │  └──────────────────┘   │
                    └─────────────────────────┘
```

### Technology Stack

#### Frontend - Chrome Extension
- **Language**: TypeScript / Vanilla JavaScript
- **Manifest**: Chrome Extension Manifest V3
- **UI Framework**: Vanilla HTML/CSS with Tailwind CSS (via CDN)
- **Storage**: Chrome Storage API (local/sync)
- **Communication**: Chrome Runtime API, WebSocket Client
- **Build Tool**: None for MVP (direct loading), Vite/Webpack for production

**Why Chrome Extension:**
- Bypasses TikTok's anti-bot detection (runs in user's actual browser)
- Uses user's logged-in session (no auth needed)
- Direct DOM access to TikTok's page
- Can capture screenshots natively
- No CORS issues
- Better UX than Playwright UI

#### Backend - FastAPI
- **Framework**: FastAPI 0.104.1+
- **Language**: Python 3.11+
- **Server**: Uvicorn (ASGI server) with WebSocket support
- **Async**: Native async/await support
- **Validation**: Pydantic v2 for data validation
- **CORS**: fastapi.middleware.cors for cross-origin requests

**Endpoints:**
```python
POST   /api/classify          # Classify video content
POST   /api/session/start     # Start calibration session
POST   /api/session/stop      # Stop calibration session
GET    /api/session/{id}      # Get session details
WS     /ws/session/{id}       # WebSocket for real-time updates
GET    /api/health            # Health check
```

**Why FastAPI:**
- Fastest Python framework (comparable to Node.js/Go)
- Native async/await for concurrent LLM requests
- Built-in WebSocket support
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Easy deployment to Render/Railway

#### Browser Automation - Playwright (Fallback Only)
- **Library**: Playwright for Python 1.40.0+
- **Browser**: Chromium (headless/headful)
- **Use Case**: Fallback if extension doesn't work, or for testing

**Why Playwright over Puppeteer:**
- Better Python support than Puppeteer
- More reliable anti-detection features
- Auto-waiting for elements
- Better debugging tools

**Note**: Extension is primary approach; Playwright is fallback.

#### Real-time Communication
- **Protocol**: WebSockets (RFC 6455)
- **Library**: FastAPI WebSocket support (built-in)
- **Client**: Native WebSocket API in JavaScript
- **Format**: JSON messages

**Message Types:**
```typescript
// Client -> Server
{ type: "session_start", categories: string[], threshold: number }
{ type: "session_stop" }
{ type: "ping" }

// Server -> Client
{ type: "stats_update", videosProcessed: number, matchesFound: number, matchRate: number }
{ type: "video_classified", isMatch: boolean, category: string, confidence: number }
{ type: "session_complete", finalStats: object }
{ type: "error", message: string }
```

#### AI/ML Layer - LLM Integration

**Primary: Gemini Flash 1.5**
- **Library**: google-generativeai 0.3.1+
- **Model**: gemini-1.5-flash-latest
- **Capabilities**: Multimodal (text + images)
- **Speed**: ~500-800ms per classification
- **Cost**: $0.00001875 per image + $0.000125 per 1K tokens (extremely cheap)
- **Rate Limit**: 60 requests/minute (free tier)

**Fallback 1: GPT-4o-mini**
- **Library**: openai 1.3.0+
- **Model**: gpt-4o-mini
- **Speed**: ~600-1000ms
- **Cost**: $0.01 per 1K tokens
- **Use Case**: If Gemini API fails or hits rate limit

**Fallback 2: Claude 3 Haiku**
- **Library**: anthropic 0.7.0+
- **Model**: claude-3-haiku-20240307
- **Speed**: ~400-600ms (fastest)
- **Cost**: $0.00025 per 1K tokens
- **Use Case**: If both Gemini and OpenAI fail

**Fallback 3: Local Mistral**
- **Library**: ollama-python (optional)
- **Model**: mistral:7b-instruct
- **Speed**: 2-4 seconds (local inference)
- **Cost**: Free (runs locally)
- **Use Case**: No API keys available

**Classification Prompt Template:**
```python
SYSTEM_PROMPT = """You are a TikTok content classifier. Analyze the video screenshot and metadata to determine which category it belongs to.

Categories:
- Thirst Traps: Attractive people showing off their bodies, flirty content, dating advice
- Skits: Comedy sketches, acting, roleplay, funny scenarios
- Brainrot: Memes, chaotic edits, Gen Z humor, unhinged content
- Tech: Programming, gadgets, software, AI, tutorials, tech reviews
- News: Current events, politics, world news, breaking news
- Edits: AMVs, fan edits, transitions, video editing showcases
- Photography: Photo tips, camera gear, composition, photo showcases

Return JSON: {"category": "Tech", "confidence": 0.85, "reasoning": "Shows code on screen"}
"""

USER_PROMPT = """
Caption: {caption}
Hashtags: {hashtags}
Username: @{username}
[Image attached]

Which category does this video belong to?
"""
```

#### Data Layer

**MVP: SQLite**
- **Library**: sqlite3 (Python standard library)
- **File**: `scrollmaxxr.db`
- **Tables**:
  - `sessions` (id, user_id, start_time, end_time, categories, stats)
  - `classifications` (id, session_id, video_url, category, confidence, timestamp)
  - `users` (id, extension_id, created_at)

**Production: PostgreSQL**
- **Library**: asyncpg 0.29.0+
- **ORM**: SQLAlchemy 2.0+ with async support
- **Hosting**: Supabase (free tier) or Neon (serverless Postgres)

**Why SQLite for MVP:**
- Zero configuration
- File-based (easy to demo)
- Fast enough for hackathon
- Easy migration to Postgres later

#### Styling - Tailwind CSS
- **Version**: Tailwind CSS 3.4+
- **Setup**: CDN for extension, PostCSS for Next.js
- **Preset**: Default + custom purple/pink gradient theme
- **Dark Mode**: class-based dark mode (default)

**Why Tailwind:**
- Rapid prototyping
- Consistent design system
- Small bundle size with purging
- Great DX for hackathons

#### UI Components - shadcn/ui
- **Library**: shadcn/ui (Radix UI primitives + Tailwind)
- **Components**: Button, Card, Checkbox, Progress, Badge, Dialog, Tabs
- **Version**: Latest (installed via CLI)
- **Customization**: Full control over component source

**Why shadcn/ui:**
- Copy-paste components (no npm bloat)
- Built on Radix UI (accessible by default)
- Fully customizable
- Beautiful out of the box

#### Icons - Lucide React
- **Library**: lucide-react 0.294.0+
- **Usage**: `<Play />`, `<Pause />`, `<TrendingUp />`
- **Style**: Consistent stroke-based icons

#### API Integration - RapidAPI TikTok Scraper (Optional)
- **Service**: RapidAPI TikTok Data Scraper
- **Use Case**: Get additional metadata (views, likes, comments) if needed
- **Cost**: 500 requests/month free
- **Priority**: Low (not needed for MVP)

---

## System Components

### 1. Chrome Extension (User's Browser)

#### A. Popup UI (Extension Control Panel)
**File**: `extension/popup/popup.html`

**Responsibilities:**
- Display category selection checkboxes
- Show Start/Stop buttons
- Display real-time stats (videos processed, matches found, match rate)
- Show progress bar
- Handle user input

**Technologies:**
- HTML5 for structure
- CSS3 + Tailwind for styling
- Vanilla JavaScript for logic
- Chrome Storage API for saving preferences

**Key Functions:**
```javascript
// popup.js
async function startCalibration() {
  const categories = getSelectedCategories();
  await chrome.storage.local.set({ calibrationActive: true, categories });
  await chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: "start", categories });
  });
  connectWebSocket();
}

function updateStats(stats) {
  document.getElementById('videos-processed').textContent = stats.videosProcessed;
  document.getElementById('matches-found').textContent = stats.matchesFound;
  document.getElementById('match-rate').textContent = `${stats.matchRate}%`;
}
```

#### B. Content Script (TikTok Page Interaction)
**File**: `extension/content/content.js`

**Responsibilities:**
- Detect when TikTok page loads
- Observe video changes (IntersectionObserver)
- Extract video metadata (caption, hashtags, username)
- Capture screenshot of current video frame
- Send data to background worker
- Execute actions (like, scroll)
- Handle errors and edge cases

**Technologies:**
- Vanilla JavaScript
- Chrome Runtime API
- MutationObserver for DOM changes
- IntersectionObserver for video detection
- Canvas API for screenshot capture

**Key Functions:**
```javascript
// content.js
function observeVideoChanges() {
  const videoContainer = document.querySelector('[data-e2e="recommend-list"]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        processCurrentVideo();
      }
    });
  }, { threshold: 0.8 });
  
  // Observe video elements
  videoContainer.querySelectorAll('video').forEach(video => {
    observer.observe(video.parentElement);
  });
}

async function extractVideoData() {
  const caption = document.querySelector('[data-e2e="video-desc"]')?.textContent || '';
  const hashtags = Array.from(document.querySelectorAll('a[href*="/tag/"]'))
    .map(el => el.textContent);
  const username = document.querySelector('[data-e2e="video-author"]')?.textContent || '';
  const videoUrl = window.location.href;
  
  // Capture screenshot
  const video = document.querySelector('video');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0);
  const screenshot = canvas.toDataURL('image/jpeg', 0.7);
  
  return { caption, hashtags, username, videoUrl, screenshot };
}

async function likeVideo() {
  const likeButton = document.querySelector('[data-e2e="like-icon"]');
  if (likeButton && !likeButton.classList.contains('active')) {
    likeButton.click();
    await randomDelay(500, 1000);
  }
}

async function scrollToNextVideo() {
  window.scrollBy({ top: window.innerHeight, behavior: 'smooth' });
  await randomDelay(1500, 2500);
}

function randomDelay(min, max) {
  const delay = Math.random() * (max - min) + min;
  return new Promise(resolve => setTimeout(resolve, delay));
}
```

#### C. Background Service Worker (API Communication)
**File**: `extension/background/background.js`

**Responsibilities:**
- Maintain WebSocket connection to backend
- Forward messages between content script and backend
- Handle API requests to /api/classify
- Manage session state
- Handle errors and retries

**Technologies:**
- Service Worker API (Manifest V3)
- Fetch API for REST requests
- WebSocket API for real-time communication

**Key Functions:**
```javascript
// background.js
let ws = null;
let sessionId = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'classify') {
    classifyVideo(message.data).then(sendResponse);
    return true; // async response
  }
});

async function classifyVideo(videoData) {
  const response = await fetch('http://localhost:8000/api/classify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(videoData)
  });
  return await response.json();
}

function connectWebSocket() {
  ws = new WebSocket('ws://localhost:8000/ws/session');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Forward to popup for UI update
    chrome.runtime.sendMessage({ type: 'stats_update', data });
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    // Retry connection
    setTimeout(connectWebSocket, 5000);
  };
}
```

---

### 2. FastAPI Backend

#### A. REST API Endpoints

**File**: `backend/api/routes.py`

**Responsibilities:**
- Handle video classification requests
- Manage calibration sessions
- Return classification results
- Health checks

**Endpoint Details:**

```python
# POST /api/classify
@app.post("/api/classify")
async def classify_video(video_data: VideoData):
    """
    Classify a TikTok video using LLM.
    
    Input:
    {
      "caption": str,
      "hashtags": list[str],
      "username": str,
      "videoUrl": str,
      "screenshot": str (base64),
      "selectedCategories": list[str]
    }
    
    Output:
    {
      "isMatch": bool,
      "category": str,
      "confidence": float,
      "reasoning": str
    }
    """
    try:
        # Decode screenshot
        image_data = base64.b64decode(video_data.screenshot.split(',')[1])
        
        # Call LLM classifier
        result = await classifier.classify(
            image=image_data,
            caption=video_data.caption,
            hashtags=video_data.hashtags,
            username=video_data.username,
            target_categories=video_data.selectedCategories
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### B. WebSocket Server

**File**: `backend/api/websocket.py`

**Responsibilities:**
- Maintain persistent connection with extension
- Send real-time stats updates
- Handle session lifecycle
- Broadcast events

**Implementation:**
```python
# WS /ws/session/{session_id}
@app.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Add to active connections
    session_manager.connect(session_id, websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            if data['type'] == 'stats_update':
                # Broadcast to all connected clients for this session
                await session_manager.broadcast(session_id, data)
                
            elif data['type'] == 'ping':
                await websocket.send_json({'type': 'pong'})
                
    except WebSocketDisconnect:
        session_manager.disconnect(session_id)
```

#### C. LLM Classifier Integration

**File**: `backend/classifier/llm_classifier.py`

**Responsibilities:**
- Interface with multiple LLM providers
- Implement fallback logic
- Parse LLM responses
- Calculate confidence scores
- Handle rate limits

**Implementation:**
```python
class LLMClassifier:
    def __init__(self):
        self.gemini = genai.GenerativeModel('gemini-1.5-flash')
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def classify(self, image: bytes, caption: str, hashtags: list[str], 
                      username: str, target_categories: list[str]) -> dict:
        # Try Gemini first (fastest + cheapest)
        try:
            result = await self._classify_with_gemini(
                image, caption, hashtags, username, target_categories
            )
            return result
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")
            
            # Fallback to GPT-4o-mini
            try:
                result = await self._classify_with_openai(
                    image, caption, hashtags, username, target_categories
                )
                return result
            except Exception as e:
                logger.warning(f"OpenAI failed: {e}")
                
                # Final fallback to rule-based
                return self._rule_based_classify(caption, hashtags, target_categories)
    
    async def _classify_with_gemini(self, image, caption, hashtags, username, categories):
        # Create prompt
        prompt = self._build_prompt(caption, hashtags, username, categories)
        
        # Prepare image
        img = Image.open(io.BytesIO(image))
        
        # Generate
        response = await self.gemini.generate_content_async([prompt, img])
        
        # Parse JSON response
        result = json.loads(response.text)
        
        # Check if category is in target categories
        is_match = result['category'] in categories
        
        return {
            'isMatch': is_match,
            'category': result['category'],
            'confidence': result['confidence'],
            'reasoning': result.get('reasoning', '')
        }
```

#### D. Session Management

**File**: `backend/session/manager.py`

**Responsibilities:**
- Track active calibration sessions
- Store session state and statistics
- Calculate metrics (match rate, time saved)
- Detect completion conditions

**Implementation:**
```python
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.connections = {}
        
    def create_session(self, categories: list[str], threshold: float = 0.7) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'categories': categories,
            'threshold': threshold,
            'videosProcessed': 0,
            'matchesFound': 0,
            'matchRate': 0.0,
            'startTime': datetime.now(),
            'status': 'active',
            'recentMatches': []  # Last 20 videos for rolling average
        }
        return session_id
    
    def update_stats(self, session_id: str, is_match: bool):
        session = self.sessions[session_id]
        session['videosProcessed'] += 1
        if is_match:
            session['matchesFound'] += 1
        
        # Update match rate
        session['matchRate'] = session['matchesFound'] / session['videosProcessed']
        
        # Track recent matches for completion detection
        session['recentMatches'].append(is_match)
        if len(session['recentMatches']) > 20:
            session['recentMatches'].pop(0)
        
        # Check completion condition
        if len(session['recentMatches']) == 20:
            recent_rate = sum(session['recentMatches']) / 20
            if recent_rate >= session['threshold']:
                session['status'] = 'complete'
                
    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.connections:
            for websocket in self.connections[session_id]:
                await websocket.send_json(message)
```

---

### 3. Content Classification System

#### Category Definitions

```python
CATEGORIES = {
    "Thirst Traps": {
        "description": "Attractive people showing off their bodies, flirty content, dating advice, fashion try-ons, fitness flexing",
        "keywords": ["gym", "outfit", "hot", "cute", "date", "boyfriend", "girlfriend"],
        "visual_cues": ["mirror selfies", "workout videos", "closeup face shots", "revealing clothing"]
    },
    "Skits": {
        "description": "Comedy sketches, acting, roleplay, funny scenarios, POV content",
        "keywords": ["pov", "when", "acting", "character", "skit", "comedy"],
        "visual_cues": ["multiple people", "exaggerated expressions", "text overlays with dialogue"]
    },
    "Brainrot": {
        "description": "Memes, chaotic edits, Gen Z humor, unhinged content, shitposts, surreal humor",
        "keywords": ["💀", "fr fr", "no cap", "sigma", "rizz", "skibidi", "ohio"],
        "visual_cues": ["fast cuts", "distorted audio", "multiple memes overlaid", "chaotic energy"]
    },
    "Tech": {
        "description": "Programming, gadgets, software, AI, tutorials, tech reviews, coding",
        "keywords": ["code", "programming", "ai", "software", "tech", "tutorial", "developer"],
        "visual_cues": ["code on screen", "tech products", "terminal/IDE", "diagrams"]
    },
    "News": {
        "description": "Current events, politics, world news, breaking news, investigative journalism",
        "keywords": ["breaking", "news", "politics", "election", "economy", "war"],
        "visual_cues": ["news graphics", "serious tone", "facts/statistics", "news clips"]
    },
    "Edits": {
        "description": "AMVs, fan edits, transitions, video editing showcases, aesthetic videos",
        "keywords": ["edit", "amv", "transition", "cc", "after effects", "preset"],
        "visual_cues": ["fast cuts", "color grading", "transitions", "music sync"]
    },
    "Photography": {
        "description": "Photo tips, camera gear, composition, photo showcases, tutorials",
        "keywords": ["photography", "camera", "lens", "lightroom", "portrait", "composition"],
        "visual_cues": ["cameras/lenses", "photo editing software", "beautiful landscapes", "studio setups"]
    }
}
```

#### Multimodal Analysis Pipeline

```python
async def analyze_content(image: bytes, text: str, hashtags: list) -> dict:
    """
    Combine visual and textual analysis for classification.
    """
    # 1. Visual Analysis (via LLM)
    visual_features = await analyze_image(image)
    
    # 2. Text Analysis (simple NLP)
    text_features = analyze_text(text, hashtags)
    
    # 3. Combine signals
    combined_confidence = (
        visual_features['confidence'] * 0.7 +  # Images more reliable
        text_features['confidence'] * 0.3      # Text can be misleading
    )
    
    # 4. Final decision
    if visual_features['category'] == text_features['category']:
        return {
            'category': visual_features['category'],
            'confidence': min(combined_confidence * 1.2, 1.0),  # Boost if both agree
            'method': 'multimodal_agreement'
        }
    else:
        # Trust visual more
        return {
            'category': visual_features['category'],
            'confidence': visual_features['confidence'],
            'method': 'visual_priority'
        }
```

#### Confidence Scoring

```python
def calculate_confidence(llm_response: dict, text_signals: dict) -> float:
    """
    Calculate final confidence score based on multiple signals.
    """
    base_confidence = llm_response.get('confidence', 0.5)
    
    # Boost factors
    if len(text_signals['matched_keywords']) > 3:
        base_confidence *= 1.1  # Strong text signals
    
    if llm_response.get('reasoning') and len(llm_response['reasoning']) > 50:
        base_confidence *= 1.05  # LLM provided detailed reasoning
    
    # Penalty factors
    if base_confidence < 0.4:
        base_confidence *= 0.8  # LLM is very uncertain
    
    # Clamp to [0, 1]
    return min(max(base_confidence, 0.0), 1.0)
```

#### Fallback Strategies

1. **LLM Fallback Chain**: Gemini → GPT-4o-mini → Claude Haiku → Rule-based
2. **Rule-based Classifier**: If all LLMs fail, use keyword matching + heuristics
3. **Confidence Threshold**: If confidence < 0.3, skip video (don't like or dislike)
4. **Error Handling**: If classification fails 3 times in a row, pause and notify user

---

### 4. Next.js Webapp (Phase 2 - Optional)

#### A. Landing Page
**File**: `webapp/app/page.tsx`

**Sections:**
1. Hero with video demo
2. How it works (3-step process)
3. Features grid
4. Social proof / stats
5. FAQ
6. CTA to install extension

**Technologies:**
- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- Framer Motion for animations
- shadcn/ui components

#### B. Dashboard
**File**: `webapp/app/dashboard/page.tsx`

**Features:**
- Session history table
- Analytics charts (Recharts)
- Category distribution pie chart
- Time saved calculator
- Export data

#### C. Analytics Visualization
**Libraries:**
- Recharts for charts
- react-table for data tables
- date-fns for date formatting

---

## Data Flow

### Detailed Workflow (Step-by-Step)

```
1. USER INITIATES CALIBRATION
   ├─ Opens extension popup on TikTok page
   ├─ Selects desired category from dropdown (e.g., "Tech") OR enters custom description
   ├─ Clicks "Start Calibration"
   └─ Extension stores preferences in Chrome Storage

2. EXTENSION ESTABLISHES CONNECTION
   ├─ Background worker creates WebSocket connection to backend
   │  ws://localhost:8000/ws/session
   ├─ Backend creates new session with unique ID
   ├─ Backend returns session ID
   └─ Connection confirmed, ready state

3. CONTENT SCRIPT ACTIVATES
   ├─ Receives "start" message from popup
   ├─ Sets up IntersectionObserver on video container
   ├─ Detects current video in viewport
   └─ Begins processing loop

4. VIDEO DATA CAPTURE
   ├─ Extract caption from [data-e2e="video-desc"]
   ├─ Extract hashtags from <a href="/tag/...">
   ├─ Extract username from [data-e2e="video-author"]
   ├─ Extract video URL from window.location.href
   ├─ Capture screenshot:
   │  ├─ Get <video> element
   │  ├─ Draw current frame to <canvas>
   │  ├─ Convert to base64 JPEG (quality: 0.7)
   │  └─ Screenshot size: ~50-100KB
   └─ Package data into JSON object

5. SEND TO BACKEND FOR CLASSIFICATION
   ├─ Content script → Background worker (chrome.runtime.sendMessage)
   ├─ Background worker → FastAPI (POST /api/classify)
   │  {
   │    "caption": "Learning React hooks! 🔥 #coding #programming",
   │    "hashtags": ["coding", "programming", "webdev"],
   │    "username": "techbro123",
   │    "videoUrl": "https://tiktok.com/@techbro123/video/123...",
   │    "screenshot": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
   │    "category": "Tech",
   │    "categoryDescription": "Tech: Programming, gadgets, software, AI, tutorials, tech reviews, coding"
   │  }
   └─ Request time: ~10-50ms (network)

6. BACKEND PROCESSES REQUEST
   ├─ FastAPI receives request
   ├─ Validates data with Pydantic
   ├─ Decodes base64 screenshot to bytes
   ├─ Calls LLMClassifier.classify()
   └─ Processing begins

7. LLM CLASSIFICATION
   ├─ Try Gemini Flash 1.5:
   │  ├─ Build prompt with user's desired content description
   │  ├─ Attach image and text metadata
   │  ├─ Send to Gemini API
   │  ├─ Response time: ~500-800ms
   │  └─ Parse JSON response
   │
   ├─ LLM analyzes:
   │  ├─ Visual: Code editor on screen, person typing
   │  ├─ Text: "Learning React hooks" + #coding
   │  ├─ User wants: "Tech: Programming, gadgets, software, AI"
   │  └─ Decision: isMatch=true, Confidence=0.92
   │
   └─ Return result with reasoning

8. RETURN CLASSIFICATION RESULT
   ├─ Backend → Background worker (HTTP response)
   │  {
   │    "isMatch": true,
   │    "category": "Tech",
   │    "confidence": 0.92,
   │    "reasoning": "Video shows code editor with React code, caption mentions programming"
   │  }
   ├─ Response time: ~600-1000ms total
   └─ Background worker → Content script (chrome.runtime.sendMessage)

9. CONTENT SCRIPT EXECUTES ACTION
   ├─ Receives classification result
   │
   ├─ IF isMatch == true:
   │  ├─ Find like button: document.querySelector('[data-e2e="like-icon"]')
   │  ├─ Click like button
   │  ├─ Wait random delay: 500-1000ms (human-like)
   │  ├─ Scroll to next video: window.scrollBy({ top: innerHeight })
   │  └─ Wait random delay: 1500-2500ms
   │
   └─ IF isMatch == false:
      ├─ Skip liking
      ├─ Scroll to next video immediately
      └─ Wait shorter delay: 800-1500ms

10. UPDATE STATS
    ├─ Content script sends stats to background worker
    ├─ Background worker sends via WebSocket to backend
    │  { type: "stats_update", isMatch: true }
    ├─ Backend updates SessionManager:
    │  ├─ videosProcessed++
    │  ├─ matchesFound++ (if match)
    │  ├─ Recalculate matchRate
    │  └─ Check completion condition
    │
    └─ Backend broadcasts stats via WebSocket:
       { 
         type: "stats_update",
         videosProcessed: 23,
         matchesFound: 15,
         matchRate: 0.65,
         status: "active"
       }

11. UPDATE UI IN REAL-TIME
    ├─ Background worker receives WebSocket message
    ├─ Forward to popup: chrome.runtime.sendMessage()
    ├─ Popup updates DOM:
    │  ├─ Videos Processed: 23
    │  ├─ Matches Found: 15
    │  ├─ Match Rate: 65%
    │  └─ Progress bar: 65% filled
    └─ Smooth animations (CSS transitions)

12. REPEAT LOOP (Steps 3-11)
    ├─ Process next video
    ├─ Continue until completion condition met
    └─ Target: 70% match rate over last 20 videos

13. COMPLETION DETECTION
    ├─ Backend checks after each classification:
    │  ├─ Has processed at least 20 videos?
    │  ├─ Last 20 videos have ≥70% match rate?
    │  └─ IF yes: session status = "complete"
    │
    ├─ Backend sends completion message:
    │  {
    │    type: "session_complete",
    │    finalStats: {
    │      videosProcessed: 47,
    │      matchesFound: 35,
    │      matchRate: 0.74,
    │      duration: "2m 34s",
    │      timeSaved: "12 minutes"
    │    }
    │  }
    └─ Extension stops processing

14. USER SEES RESULTS
    ├─ Popup shows success message
    ├─ Displays final stats
    ├─ Shows "Time saved" calculation
    ├─ Offers to view analytics
    └─ User can now scroll normally and enjoy calibrated FYP
```

### Performance Metrics

- **Time per video**: 1-2 seconds (including classification + action + delay)
- **Videos to calibrate**: 40-60 videos average
- **Total time**: 2-4 minutes
- **Accuracy target**: 70%+ correct classifications
- **Network usage**: ~2-5MB per session (mostly screenshots)

---

## Technology Justification

### Why Chrome Extension Over Playwright?

**Advantages:**
1. **No Bot Detection**: Runs in user's actual browser with their logged-in session
2. **Better UX**: User can see it happening in real-time
3. **No Auth Required**: Uses user's existing TikTok cookies
4. **Lighter Weight**: No need to launch headless browser
5. **More Demo-Friendly**: Can show live in presentation

**Trade-offs:**
- Requires users to install extension
- Chrome Web Store review process (can sideload for hackathon)

### Why Multiple LLMs?

**Reasons for fallback chain:**
1. **Rate Limits**: Free tiers have limits (60 req/min for Gemini)
2. **Reliability**: APIs can go down during hackathon
3. **Content Policy**: Some LLMs may refuse to classify "Thirst Traps"
4. **Cost Optimization**: Use cheapest API first (Gemini), upgrade if needed
5. **Speed Variation**: Different models have different latencies

### Why FastAPI Over Node.js/Flask?

**FastAPI advantages:**
1. **Speed**: Comparable to Node.js, faster than Flask
2. **Async Native**: async/await built-in, perfect for I/O-bound LLM calls
3. **Type Safety**: Pydantic validation catches bugs early
4. **WebSocket Support**: Built-in, no extra libraries
5. **Auto Docs**: OpenAPI/Swagger UI automatically generated
6. **Python Ecosystem**: Better LLM library support (Langchain, etc.)

### Why WebSockets Over Polling?

**WebSocket advantages:**
1. **Real-time**: Instant updates, no 1-2 second delay
2. **Efficient**: Single persistent connection vs. repeated HTTP requests
3. **Lower Latency**: No request/response overhead
4. **Better UX**: Smooth, live updates feel more professional
5. **Scales Better**: Server can push to multiple clients

### Why Next.js for Webapp?

**Next.js advantages:**
1. **Fast Development**: File-based routing, zero config
2. **SEO Friendly**: Server-side rendering for landing page
3. **Easy Deployment**: One-click Vercel deployment
4. **Great DX**: Hot reload, TypeScript support, ESLint built-in
5. **Modern Stack**: App Router, Server Components, etc.

---

## Development Constraints

### Time Constraints (24-36 hours)

**Hackathon Timeline:**
- **Hours 0-6**: Core extension + backend setup
- **Hours 7-12**: LLM integration + classification
- **Hours 13-18**: Automation logic + polish
- **Hours 19-24**: Webapp (if time permits) + debugging
- **Hours 25-36**: Testing, demo prep, video recording

**Scope Cuts if Behind:**
1. Drop Next.js webapp (keep extension only)
2. Remove analytics/dashboard
3. Simplify to single LLM (Gemini only)
4. Reduce category count (4 categories instead of 7)
5. Skip confidence scoring (binary yes/no)

### TikTok Anti-Bot Measures

**Challenges:**
1. **Aggressive rate limiting**: Too fast = IP ban
2. **Bot detection**: Selenium/Playwright patterns detected
3. **CAPTCHA**: Sometimes triggered on automated actions
4. **DOM obfuscation**: Class names change regularly
5. **API protection**: No public API for content

**Mitigations:**
1. **Human-like delays**: Random 1-3 second pauses
2. **Use real browser**: Chrome extension bypasses detection
3. **Respect rate limits**: Max 20-30 videos/minute
4. **Graceful degradation**: Handle CAPTCHAs by pausing
5. **Fallback selectors**: Use multiple ways to find elements

### LLM API Constraints

**Rate Limits:**
- Gemini Free: 60 requests/minute
- OpenAI Free: 3 requests/minute (need paid)
- Claude Free: 5 requests/minute

**Cost Estimates (100 videos):**
- Gemini: ~$0.02 (extremely cheap)
- GPT-4o-mini: ~$0.10
- Claude Haiku: ~$0.03

**Strategies:**
- Cache classifications for repeated videos
- Batch requests when possible
- Use cheapest model first

### Chrome Extension Constraints

**Manifest V3 Requirements:**
- Service workers instead of background pages
- Limited persistent state
- Stricter content security policy
- Host permissions required

**Hackathon Workaround:**
- Load unpacked extension (no store approval needed)
- Use localhost for backend (no HTTPS required)
- Side-load on demo machine

### Content Policy Compliance

**Potential Issues:**
1. **"Thirst Traps" category**: Some LLMs may refuse due to policy
2. **Automated actions**: TikTok TOS violation (gray area)
3. **Data scraping**: Not selling data, just classifying

**Solutions:**
1. Rename sensitive categories ("Fashion" instead of "Thirst Traps")
2. Add disclaimer: "For educational purposes only"
3. Don't store/sell user data
4. Respect robots.txt (not scraping at scale)

---

## Success Metrics

### Demo Success (Must-Have)

- [ ] Extension loads without errors
- [ ] Can connect to TikTok and detect videos
- [ ] Backend API responds within 2 seconds
- [ ] Classification accuracy ≥60% (acceptable for demo)
- [ ] Successfully processes 20+ videos in demo
- [ ] Real-time stats update smoothly
- [ ] Judges understand the concept
- [ ] No crashes during 5-minute demo

### Technical Success (Nice-to-Have)

- [ ] Classification accuracy ≥75%
- [ ] Average response time <1 second
- [ ] Processes 50+ videos without errors
- [ ] WebSocket connection stays alive
- [ ] Handles edge cases gracefully
- [ ] Clean, readable code
- [ ] Good error messages

### Hackathon Success (Winning Criteria)

- [ ] **Weird Factor**: Definitely weird (automated social media manipulation)
- [ ] **Practical**: Actually useful (saves 20+ minutes)
- [ ] **Technical Impressiveness**: Multi-component system, AI integration, real-time
- [ ] **Polish**: Looks good, works smoothly
- [ ] **Demo-ability**: Can show live in 3 minutes
- [ ] **Story**: Relatable problem, clever solution
- [ ] **Judges Reaction**: "Wait, that's actually cool"

### Post-Hackathon Metrics

- [ ] GitHub stars (if open-sourced)
- [ ] Chrome Web Store installs (if published)
- [ ] User feedback / testimonials
- [ ] Portfolio piece quality
- [ ] Press mentions (ProductHunt, etc.)

---

## Future Enhancements (Post-Hackathon)

### Phase 3 Features
- Multi-platform support (Instagram Reels, YouTube Shorts)
- Custom category creation
- ML model fine-tuning on user feedback
- Scheduled calibration (run nightly)
- Undo calibration (reset FYP)
- Share category profiles with friends
- Browser extension for Firefox/Edge

### Monetization Ideas
- Freemium model (5 sessions/month free)
- API for developers
- White-label solution for brands
- Premium analytics dashboard
- Affiliate revenue from tech products shown

---

**Last Updated:** November 9, 2025

