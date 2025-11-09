"""
API Routes for ScrollMaxxr Backend
Handles video classification requests.
"""

from fastapi import APIRouter, HTTPException
from models.schemas import VideoData, ClassificationResult
import base64
from PIL import Image
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["classification"])


@router.post("/classify", response_model=ClassificationResult)
async def classify_video(video_data: VideoData):
    """
    Classify a TikTok video using LLM.
    
    Args:
        video_data: VideoData containing caption, hashtags, screenshot, etc.
    
    Returns:
        ClassificationResult with isMatch, category, confidence, and reasoning
    """
    try:
        logger.info(f"Classifying video: {video_data.videoUrl}")
        logger.info(f"Category: {video_data.category}")
        logger.info(f"Description: {video_data.categoryDescription}")
        
        # Decode screenshot from base64
        if ',' in video_data.screenshot:
            # Remove data URL prefix if present
            image_data = video_data.screenshot.split(',')[1]
        else:
            image_data = video_data.screenshot
        
        try:
            image_bytes = base64.b64decode(image_data)
            logger.info(f"Screenshot decoded: {len(image_bytes)} bytes")
        except Exception as e:
            logger.error(f"Failed to decode screenshot: {e}")
            raise HTTPException(status_code=400, detail="Invalid screenshot data")
        
        # Validate image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            logger.info(f"Image opened: {img.size} {img.format}")
        except Exception as e:
            logger.error(f"Failed to open image: {e}")
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Import and use classifier
        from classifier.llm_classifier import LLMClassifier
        
        classifier = LLMClassifier()
        result = await classifier.classify(
            image=image_bytes,
            caption=video_data.caption,
            hashtags=video_data.hashtags,
            username=video_data.username,
            category=video_data.category,
            category_description=video_data.categoryDescription
        )
        
        logger.info(f"Classification result: {result}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error classifying video: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "API is working! 🎯",
        "endpoints": {
            "classify": "/api/classify",
            "health": "/api/health"
        }
    }

