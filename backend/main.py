"""
ScrollMaxxr Backend - FastAPI Application
Entry point for the TikTok FYP Calibrator backend server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ScrollMaxxr API",
    description="TikTok FYP Calibrator - AI-powered content classification API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in allowed_origins else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from api.routes import router as api_router

# Include routers
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API welcome message"""
    return {
        "message": "ScrollMaxxr API is running! 🎯",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on server startup"""
    print("=" * 50)
    print("🎯 ScrollMaxxr Backend Starting...")
    print(f"📍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🔑 Gemini API Key: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Missing'}")
    print(f"🔑 OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '⚠️  Optional'}")
    print("=" * 50)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on server shutdown"""
    print("🛑 ScrollMaxxr Backend Shutting Down...")

# Run server
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n🚀 Starting server at http://{host}:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable hot-reload in development
        log_level="info"
    )

