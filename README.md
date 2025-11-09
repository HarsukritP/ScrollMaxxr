# ScrollMaxxr - TikTok FYP Calibrator

> **Stop scrolling past content you hate. Let AI train your FYP in 2 minutes.**

An AI-powered Chrome extension that automatically calibrates your TikTok For You Page by intelligently analyzing and engaging with your desired content categories.

**Built for Go On Hacks 2025**

---

## What It Does

ScrollMaxxr automates the tedious process of training your TikTok algorithm. Simply select what content you want to see (or describe it in your own words), hit start, and let our AI agent run in the background:

- **Runs in a headless browser** - You don't need TikTok open!
- Scrolls through TikTok automatically using Playwright
- Analyzes each video using multimodal AI (GPT-5-nano)
- Likes videos that match your preferences
- Skips videos you don't want
- Provides real-time progress updates via WebSocket
- Completes when your FYP is optimized (70% match rate)

**Result:** A perfectly curated For You Page in 2-3 minutes instead of 30+ minutes of manual scrolling.

**Architecture:** Chrome extension extracts your TikTok cookies → Backend launches Playwright headless browser → Playwright navigates TikTok with your session → AI classifies videos → Actions executed → Stats stream back to extension.

---

## Quick Start

### Prerequisites

- **Node.js** 18+ (for webapp, optional)
- **Python** 3.11+
- **Chrome Browser**
- **API Keys:**
  - [Google AI Studio](https://makersuite.google.com/app/apikey) for Gemini API (free tier available)
  - [OpenAI API](https://platform.openai.com/api-keys) for GPT-4o-mini (fallback, optional)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/HarsukritP/ScrollMaxxr.git
cd ScrollMaxxr
```

#### 2. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (includes Playwright)
pip install -r requirements.txt

# Install Playwright Chromium browser (~200MB)
playwright install chromium

# Create .env file
cp .env.example .env

# Add your API key to .env
# OPENAI_API_KEY=your_openai_api_key_here
```

**Or use the automated installer:**

```bash
./INSTALL.sh
```

#### 3. Start Backend Server

```bash
# Make sure you're in backend/ directory with venv activated
python main.py

# Server will start at http://localhost:8000
# You should see: "Uvicorn running on http://0.0.0.0:8000"
```

#### 4. Load Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `extension/` folder from this project
5. You should see the ScrollMaxxr icon in your extensions

#### 5. Use the Extension

1. **Login to TikTok** at [tiktok.com](https://www.tiktok.com) (just once, to save cookies)
2. Click the **ScrollMaxxr extension icon** (don't need TikTok tab open)
3. Select a content category from dropdown (or choose "Custom" and describe your vibe)
4. Click **Start Calibration**
5. Watch the stats update in real-time!
6. **(Optional)** Close TikTok tab - calibration runs in the background on your backend server!

---

## Project Structure

```
ScrollMaxxr/
├── README.md                    # You are here
├── docs/                        # Documentation
│   ├── projectscope.md         # Complete project specification
│   ├── mvp.md                  # MVP requirements & implementation
│   └── design.md               # Design system & UI specs
│
├── extension/                   # Chrome Extension
│   ├── manifest.json           # Extension configuration
│   ├── popup/                  # Extension popup UI
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   ├── content/                # TikTok page interaction
│   │   └── content.js
│   ├── background/             # API communication
│   │   └── background.js
│   └── assets/                 # Icons and images
│       └── icons/
│
├── backend/                     # FastAPI Backend
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variables template
│   ├── api/                    # API routes
│   │   ├── routes.py          # REST endpoints
│   │   └── websocket.py       # WebSocket server
│   ├── classifier/             # LLM classification
│   │   └── llm_classifier.py  # Gemini/GPT integration
│   ├── models/                 # Data models
│   │   └── schemas.py         # Pydantic schemas
│   └── utils/                  # Helper functions
│       └── helpers.py
│
└── webapp/                      # Next.js Webapp (Phase 2, optional)
    ├── app/                    # Next.js 14 App Router
    ├── components/             # React components
    ├── public/                 # Static assets
    └── package.json
```

---

## Technology Stack

### Chrome Extension
- **Language:** JavaScript/TypeScript
- **Manifest:** V3 (latest Chrome extension standard)
- **Styling:** Tailwind CSS (via CDN)
- **Storage:** Chrome Storage API
- **Role:** Control panel & cookie extractor

### Backend
- **Framework:** FastAPI 0.104.1+
- **Language:** Python 3.11+
- **Server:** Uvicorn (ASGI)
- **Browser Automation:** Playwright (headless Chromium)
- **Anti-Bot:** playwright-stealth
- **AI/ML:** OpenAI GPT-5-nano-2025-08-07 (multimodal)
- **Real-time:** WebSocket (built-in FastAPI support)
- **Image Processing:** Pillow (PIL)

### Webapp (Phase 2)
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS 3.4+
- **UI Components:** shadcn/ui (Radix primitives)
- **Charts:** Recharts
- **Deployment:** Vercel

---

## Features

### Core Features (MVP)
- Chrome extension with intuitive UI
- Dropdown category selection (7 presets + custom)
- Custom content description (natural language)
- Real-time video classification using multimodal AI
- Automatic liking and scrolling
- Live progress tracking
- Completion detection (70% match rate)
- Human-like behavior (random delays, smooth scrolling)

### Categories
- **Thirst Traps** - Attractive people, flirty content, gym flexing
- **Skits** - Comedy sketches, POV content, acting
- **Brainrot** - Memes, chaotic edits, Gen Z humor
- **Tech** - Programming, gadgets, software, AI
- **News** - Current events, politics, journalism
- **Edits** - AMVs, fan edits, transitions
- **Photography** - Photo tips, camera gear, composition
- **Custom** - Describe your own vibe

### Phase 2 Features (Optional)
- Landing page with demo video
- Analytics dashboard
- Session history and charts
- Multiple category profiles
- Scheduled calibration
- Undo calibration

---

## How It Works

1. **You Select Your Vibe** - Choose a category or describe your ideal content
2. **AI Analyzes Videos** - Gemini Flash 1.5 examines screenshots + captions
3. **Smart Engagement** - Likes matching videos, scrolls past others
4. **Real-time Feedback** - Watch stats update as it works
5. **Perfect FYP** - Stops when 70% match rate achieved (usually 40-60 videos)

**Time Saved:** Approximately 25 minutes per calibration session

---

## Development

### Running in Development Mode

**Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
# Server runs with hot-reload at http://localhost:8000
```

**Extension:**
- Make changes to files in `extension/`
- Go to `chrome://extensions/`
- Click the refresh icon on ScrollMaxxr card
- Reload TikTok page to see changes

**Webapp (optional):**
```bash
cd webapp
npm install
npm run dev
# Opens at http://localhost:3000
```

### Testing

**Backend API Testing:**
```bash
# Health check
curl http://localhost:8000/api/health

# API documentation
open http://localhost:8000/docs
```

**Extension Testing:**
1. Load extension in Chrome
2. Open TikTok
3. Open DevTools Console (F12)
4. Start calibration and watch console logs
5. Check for errors

### Debugging Tips

- **Extension not loading?** Check `chrome://extensions/` for errors
- **API not connecting?** Ensure backend is running on port 8000
- **Classification failing?** Check your Gemini API key in `.env`
- **Videos not scrolling?** TikTok may have changed their DOM structure
- **Rate limited?** Gemini free tier has 60 requests/minute limit

---

## Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see LICENSE file for details

---

## Disclaimer

This project is for educational purposes only. Automated interaction with TikTok may violate their Terms of Service. Use at your own risk. We do not collect, store, or sell any user data.

---

## Acknowledgments

- **Go On Hacks 2025** - For the inspiration and motivation
- **Google Gemini** - For the multimodal AI API
- **OpenAI** - For GPT-4o-mini fallback support
- **FastAPI** - For the Python framework
- **TikTok** - For the addictive algorithm we're trying to fix

---

## Contact

**Project Link:** https://github.com/HarsukritP/ScrollMaxxr

**Made for Go On Hacks 2025**

---

## Roadmap

- [x] Core extension functionality
- [x] AI-powered classification
- [x] Real-time progress tracking
- [ ] Landing page
- [ ] Analytics dashboard
- [ ] Multi-platform support (Instagram Reels, YouTube Shorts)
- [ ] Chrome Web Store publication
- [ ] Firefox extension version

---

**Star this repo if you find it useful!**

