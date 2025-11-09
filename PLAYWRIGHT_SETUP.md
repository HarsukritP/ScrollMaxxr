# Playwright Setup Guide

## 🎯 **Architecture Overview**

The extension now uses **Playwright** for automation! This is the production-ready solution:

```
Extension (Control Panel) → Backend (FastAPI) → Playwright (Headless Browser) → TikTok
```

### **Key Benefits:**
- ✅ **Fully automated** - No need to keep TikTok tab open
- ✅ **Headless** - Runs in background, you can use your browser normally
- ✅ **Session injection** - Uses your real TikTok cookies/session
- ✅ **Anti-detection** - Stealth mode bypasses bot detection
- ✅ **Real-time stats** - Live updates via WebSocket

---

## 📦 **Installation**

### **1. Install Backend Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

### **2. Install Playwright Browsers**

Playwright needs to download Chromium:

```bash
playwright install chromium
```

This will download ~200MB of browser files.

### **3. Environment Variables**

Your `.env` should have:

```bash
OPENAI_API_KEY=sk-...
RAPIDAPI_KEY=your_key_here  # Optional (transcript fetching)
RAPIDAPI_HOST=tiktok-video-transcript.p.rapidapi.com
ENVIRONMENT=development
```

---

## 🚀 **How to Use**

### **Step 1: Start Backend**

```bash
cd backend
python main.py
```

You should see:
```
ScrollMaxxr Backend Starting...
Environment: development
OpenAI API Key: ✅ Set
```

### **Step 2: Login to TikTok**

1. Open your browser (Chrome/Opera/Edge)
2. Go to **https://www.tiktok.com** 
3. **Login** with your account
4. Make sure you're logged in (check your profile)

### **Step 3: Load Extension**

1. Go to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder
5. The extension icon should appear in your toolbar

### **Step 4: Start Calibration**

1. Click the extension icon
2. Select your desired content category (e.g., "Tech")
3. OR enter a custom description (e.g., "funny dog videos")
4. Click **"Start Calibration"**

### **What Happens:**

1. Extension extracts your TikTok cookies
2. Sends cookies + category to backend
3. Backend starts Playwright with your session
4. Playwright navigates to TikTok FYP
5. AI analyzes each video
6. Likes matches, scrolls non-matches
7. Live stats stream back to extension popup

---

## 🎮 **Extension Popup (Control Panel)**

The extension popup becomes a simple control panel:

```
┌─────────────────────────────────┐
│  ScrollMaxxr - FYP Calibrator   │
├─────────────────────────────────┤
│  Category: [Tech ▼]             │
│  Custom: [                 ]    │
│                                 │
│  [ Start Calibration ]          │
├─────────────────────────────────┤
│  Status: Running ⚡              │
│  Videos Processed: 15           │
│  Matches Found: 8               │
│  Match Rate: 53%                │
│                                 │
│  Current: @username/video/...   │
│                                 │
│  [ Stop ]                       │
└─────────────────────────────────┘
```

### **You DON'T need to:**
- Keep TikTok tab open
- Watch videos manually
- Interact with the page

### **Playwright does:**
- Navigate to FYP
- Extract video data
- Like/scroll
- Everything!

---

## 🔧 **Debugging**

### **Backend Logs**

Watch backend terminal for:
- `Starting Playwright browser...`
- `✅ Playwright browser ready!`
- `Processing: https://www.tiktok.com/@user/video/123`
- `Classification: isMatch=True, confidence=0.85`
- `✅ MATCH! Liking video...`

### **Extension Logs**

Open browser DevTools console (F12) → "Service Worker" tab:
- `[ScrollMaxxr BG] Starting Playwright session...`
- `[ScrollMaxxr BG] Extracted 15 cookies`
- `[ScrollMaxxr BG] Session started: abc-123-def`
- `[ScrollMaxxr BG] WebSocket connected`
- `[ScrollMaxxr BG] Stats update: {videosProcessed: 5, ...}`

### **Common Issues**

#### **"No cookies extracted"**
- Make sure you're logged into TikTok first
- Try logging out and back in
- Clear cookies and re-login

#### **"Playwright browser failed to start"**
- Run `playwright install chromium`
- Check disk space (~200MB needed)
- Check permissions

#### **"Backend not running"**
- Make sure `python main.py` is running
- Check `http://localhost:8000/docs` is accessible
- Check firewall/antivirus

#### **"Session failed to start"**
- Check backend logs for errors
- Verify OpenAI API key is set
- Try restarting backend

---

## 📊 **WebSocket Stats Stream**

The extension connects to:
```
ws://localhost:8000/api/session/ws/{session_id}
```

Receives real-time updates:
```json
{
  "session_id": "abc-123",
  "is_running": true,
  "category": "Tech",
  "stats": {
    "videosProcessed": 15,
    "matchesFound": 8,
    "matchRate": 0.53,
    "status": "running",
    "currentVideo": "https://www.tiktok.com/@user/video/123"
  },
  "lastClassification": {
    "isMatch": true,
    "confidence": 0.85,
    "reasoning": "Video contains tech review content with gadgets",
    "videoUrl": "https://www.tiktok.com/@techguy/video/456"
  }
}
```

---

## 🎯 **Next Steps**

### **Phase 1: MVP (Current)**
- ✅ Playwright automation
- ✅ Cookie injection
- ✅ Real-time stats
- ✅ Headless browser
- ⏳ Extension control panel UI
- ⏳ Full testing

### **Phase 2: Webapp**
- Dashboard with analytics
- Session history
- Multiple profiles
- Scheduled calibration
- Advanced settings

---

## 🚨 **Important Notes**

1. **Cookies are sensitive** - Never share your cookies
2. **Rate limiting** - TikTok may rate limit aggressive automation
3. **Account safety** - Use responsibly to avoid bans
4. **OpenAI costs** - Each video costs ~$0.001-0.002 (gpt-5-nano)
5. **Development only** - This is a hackathon MVP, not production-ready

---

## 🛠️ **API Endpoints**

### **Start Session**
```bash
POST /api/session/start
{
  "category": "Tech",
  "categoryDescription": "technology reviews and tutorials",
  "cookies": [...],
  "userAgent": "Mozilla/5.0..."
}
```

### **Stop Session**
```bash
POST /api/session/stop/{session_id}
```

### **Get Status**
```bash
GET /api/session/status/{session_id}
```

### **List Active Sessions**
```bash
GET /api/session/list
```

### **WebSocket**
```bash
WS /api/session/ws/{session_id}
```

---

## 📝 **Testing Checklist**

- [ ] Backend starts successfully
- [ ] Playwright browser launches
- [ ] Cookies extracted from browser
- [ ] Session starts on backend
- [ ] WebSocket connects
- [ ] Browser navigates to TikTok FYP
- [ ] Videos are detected
- [ ] AI classification works
- [ ] Likes are applied on matches
- [ ] Scrolling works
- [ ] Stats update in real-time
- [ ] Session stops cleanly
- [ ] No errors in logs

---

**Ready to test? Let's go! 🚀**

