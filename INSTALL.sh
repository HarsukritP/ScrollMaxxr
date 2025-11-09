#!/bin/bash
# ScrollMaxxr Installation Script

echo "================================================"
echo "  ScrollMaxxr - Playwright Setup"
echo "================================================"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python: $python_version"
echo ""

# Navigate to backend
cd backend || exit

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
echo ""

# Install Playwright browsers
echo "🎭 Installing Playwright Chromium browser (~200MB)..."
echo "   This may take a few minutes..."
playwright install chromium
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "   Copying env.example to .env..."
    cp env.example .env
    echo ""
    echo "📝 Please edit backend/.env and add your API keys:"
    echo "   - OPENAI_API_KEY=sk-..."
    echo "   - RAPIDAPI_KEY=... (optional)"
    echo ""
fi

echo "================================================"
echo "  ✅ Installation Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run: cd backend && python main.py"
echo "3. Load extension in Chrome (chrome://extensions)"
echo "4. Login to TikTok in your browser"
echo "5. Click extension icon and start calibration!"
echo ""
echo "📖 Read PLAYWRIGHT_SETUP.md for detailed instructions"
echo ""

