"""
Pydantic Models for Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class VideoData(BaseModel):
    """Data extracted from a TikTok video for classification"""
    caption: str = Field(..., description="Video caption text")
    hashtags: List[str] = Field(default=[], description="List of hashtags")
    username: str = Field(..., description="Video author username")
    videoUrl: str = Field(..., description="TikTok video URL")
    screenshot: str = Field(..., description="Base64 encoded screenshot")
    category: str = Field(..., description="Selected category name or 'Custom'")
    categoryDescription: str = Field(..., description="Description of desired content")


class ClassificationResult(BaseModel):
    """Result of video classification"""
    category: str = Field(..., description="Category name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reasoning: str = Field(default="", description="Explanation of classification")


class SessionCreate(BaseModel):
    """Request to create a new calibration session"""
    category: str = Field(..., description="Selected category")
    categoryDescription: str = Field(..., description="Content description")
    threshold: float = Field(default=0.70, ge=0.0, le=1.0, description="Target match rate")


class SessionStats(BaseModel):
    """Statistics for a calibration session"""
    sessionId: str = Field(..., description="Unique session ID")
    videosProcessed: int = Field(default=0, description="Total videos processed")
    matchesFound: int = Field(default=0, description="Number of matching videos")
    matchRate: float = Field(default=0.0, description="Current match rate (0-1)")
    status: str = Field(default="active", description="Session status")
    category: str = Field(..., description="Category name")
    categoryDescription: str = Field(..., description="Content description")


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment name")

