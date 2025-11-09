"""
TikTok Video Transcript Fetcher using RapidAPI
"""

import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TranscriptFetcher:
    """Fetches video transcripts from TikTok using RapidAPI"""
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = os.getenv('RAPIDAPI_HOST', 'tiktok-video-transcript.p.rapidapi.com')
        
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY not found - transcript fetching will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("TikTok transcript fetcher initialized")
    
    def get_transcript(self, video_url: str) -> Optional[str]:
        """
        Fetch transcript for a TikTok video.
        
        Args:
            video_url: Full TikTok video URL
            
        Returns:
            Transcript text if successful, None otherwise
        """
        if not self.enabled:
            logger.debug("Transcript fetching disabled (no API key)")
            return None
        
        try:
            logger.info(f"Fetching transcript for: {video_url}")
            
            # Prepare API request
            url = f"https://{self.api_host}/transcribe"
            
            querystring = {
                "url": video_url,
                "language": "eng-US",
                "timestamps": "false"
            }
            
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.api_host
            }
            
            # Make request
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract transcript from response
                # Adjust this based on the actual API response structure
                if isinstance(data, dict):
                    transcript = data.get('transcript') or data.get('text') or data.get('data')
                elif isinstance(data, str):
                    transcript = data
                else:
                    transcript = str(data)
                
                if transcript:
                    logger.info(f"Transcript fetched successfully ({len(transcript)} chars)")
                    return transcript
                else:
                    logger.warning("API returned empty transcript")
                    return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Transcript API request timed out")
            return None
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            return None


# Singleton instance
_fetcher = None

def get_fetcher() -> TranscriptFetcher:
    """Get or create the transcript fetcher instance"""
    global _fetcher
    if _fetcher is None:
        _fetcher = TranscriptFetcher()
    return _fetcher

