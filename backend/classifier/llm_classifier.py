"""
LLM Classifier for TikTok Content
Uses OpenAI GPT-5-nano for multimodal video classification.
"""

from openai import OpenAI
import os
from PIL import Image
import io
import json
from typing import List
import logging
import base64

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Category definitions (for preset categories)
CATEGORIES = {
    "Thirst Traps": "Attractive people showing off their bodies, flirty content, dating advice, gym/fitness flexing, fashion try-ons",
    "Skits": "Comedy sketches, acting, roleplay, POV content, funny scenarios, dramatic scenes",
    "Brainrot": "Memes, chaotic edits, Gen Z humor, unhinged content, surreal humor, shitposts",
    "Tech": "Programming, gadgets, software, AI, tutorials, tech reviews, coding, development",
    "News": "Current events, politics, world news, breaking news, investigative journalism",
    "Edits": "AMVs, fan edits, transitions, video editing showcases, aesthetic videos",
    "Photography": "Photo tips, camera gear, composition, photo showcases, photography tutorials, lightroom"
}

# System prompt template
SYSTEM_PROMPT = """You are a TikTok content classifier. Analyze the video screenshot and metadata to determine if it matches the user's desired content.

User wants to see: {desired_content}

Your task: Determine how well this video matches what the user wants to see.

Return ONLY a JSON object in this exact format:
{{"confidence": float 0.0-1.0, "reasoning": "brief explanation"}}

Use confidence scores:
- 0.0-0.3: Poor match or completely unrelated
- 0.3-0.5: Weak match, some relevance but not quite right
- 0.5-0.7: Good match, clearly related
- 0.7-0.9: Strong match, exactly what user wants
- 0.9-1.0: Perfect match

Focus on both visual elements in the screenshot AND text content (caption, hashtags)."""


class LLMClassifier:
    """
    Multimodal LLM classifier for TikTok content using OpenAI GPT-5 with multi-frame analysis.
    """
    
    def __init__(self):
        """Initialize the classifier with OpenAI client"""
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        logger.info("OpenAI GPT-5 classifier initialized")
    
    async def classify(
        self,
        image: bytes,
        caption: str,
        hashtags: List[str],
        username: str,
        category: str,
        category_description: str,
        video_url: str = None,
        transcript: str = None,
        all_screenshots: list = None
    ) -> dict:
        """
        Classify video content using OpenAI GPT-5 (multi-frame vision).
        
        Args:
            image: Video screenshot as bytes (fallback)
            caption: Video caption text
            hashtags: List of hashtags
            username: Video author username
            category: Selected category name or "Custom"
            category_description: Description of desired content
            video_url: Optional TikTok video URL for transcript fetching
            transcript: Optional pre-fetched transcript
        
        Returns:
            dict with category, confidence, reasoning
        """
        try:
            # DISABLED: Transcript fetching to avoid API quota issues
            # Uncomment when RapidAPI quota is available
            # if not transcript and video_url:
            #     try:
            #         from utils.transcript_fetcher import get_fetcher
            #         fetcher = get_fetcher()
            #         transcript = fetcher.get_transcript(video_url)
            #         if transcript:
            #             logger.info(f"Using transcript ({len(transcript)} chars)")
            #     except Exception as e:
            #         logger.warning(f"Failed to fetch transcript: {e}")
            
            # Determine desired content description
            if category == "Custom":
                desired_content = category_description
            else:
                # Use preset category description
                desired_content = f"{category}: {CATEGORIES.get(category, category_description)}"
            
            logger.info(f"Classifying for: {desired_content}")
            
            # Call OpenAI classification - let it fail if it fails
            result = await self._classify_with_openai(
                image, caption, hashtags, username, desired_content, category, transcript,
                all_screenshots=all_screenshots
            )
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            raise  # Re-raise the error instead of hiding it
    
    async def _classify_with_openai(
        self,
        image: bytes,
        caption: str,
        hashtags: List[str],
        username: str,
        desired_content: str,
        category: str,
        transcript: str = None,
        all_screenshots: list = None
    ) -> dict:
        """Classify using OpenAI GPT-5"""
        
        # Build system prompt
        system_prompt = SYSTEM_PROMPT.format(desired_content=desired_content)
        
        # Build user prompt with metadata
        user_prompt = f"""Caption: {caption}
Hashtags: {', '.join(hashtags) if hashtags else 'None'}
Username: @{username}"""
        
        # Add transcript if available
        if transcript:
            user_prompt += f"\nVideo Transcript: {transcript[:500]}"  # Limit to 500 chars to save tokens
        
        # If multiple screenshots provided, explain they're sequential
        if all_screenshots and len(all_screenshots) > 1:
            user_prompt += f"\n\nYou are provided with {len(all_screenshots)} sequential frames from the video, captured at 1-second intervals from the beginning. Analyze all frames together to understand the video content and progression.\n\nDoes this video match what the user wants to see?\nReturn JSON only (no other text)."
        else:
            user_prompt += "\n\nAnalyze the image and text above. Does this video match what the user wants to see?\nReturn JSON only (no other text)."
        
        # Build content array with text and images
        content_items = [
            {
                "type": "text",
                "text": user_prompt
            }
        ]
        
        # Add all screenshots if provided, otherwise use single image
        if all_screenshots and len(all_screenshots) > 0:
            for i, screenshot in enumerate(all_screenshots):
                # Extract base64 data (remove data:image/jpeg;base64, prefix if present)
                if ',' in screenshot:
                    screenshot_base64 = screenshot.split(',')[1]
                else:
                    screenshot_base64 = screenshot
                
                content_items.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{screenshot_base64}",
                        "detail": "high"  # Use high detail for better analysis
                    }
                })
                logger.info(f"Added frame {i+1}/{len(all_screenshots)} to GPT request")
        else:
            # Fallback to single image
            image_base64 = base64.b64encode(image).decode('utf-8')
            
            # Validate we have real image data (not a tiny placeholder)
            if len(image) < 1000:
                raise ValueError(f"Image data is too small ({len(image)} bytes), likely invalid screenshot")
            
            content_items.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                    "detail": "high"  # Use high detail for better analysis
                }
            })
        
        logger.info(f"Sending request to OpenAI GPT-5 with {len(content_items)-1} image(s)...")
        
        # Call OpenAI API with vision
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": content_items
                }
            ],
            max_completion_tokens=1000
        )
        
        logger.info("OpenAI response received")
        
        # Parse response
        result_text = response.choices[0].message.content
        
        # Check if response is empty
        if not result_text or not result_text.strip():
            logger.error("OpenAI returned EMPTY response!")
            logger.error(f"Full response object: {response}")
            result = {
                'confidence': 0.0,
                'reasoning': 'OpenAI returned empty response'
            }
        else:
            result_text = result_text.strip()
            logger.info(f"Raw response ({len(result_text)} chars): {result_text[:500]}")
            
            # Extract JSON (handle markdown code blocks)
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            # Parse JSON
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                logger.error(f"Full response text ({len(result_text)} chars): '{result_text}'")
                result = {
                    'confidence': 0.3,
                    'reasoning': f'Failed to parse JSON: {result_text[:100]}'
                }
        
        # Add category to result
        result['category'] = category
        
        # Validate confidence
        if 'confidence' not in result or not isinstance(result['confidence'], (int, float)):
            result['confidence'] = 0.5
        result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))
        
        # Ensure reasoning exists
        if 'reasoning' not in result:
            result['reasoning'] = 'No reasoning provided'
        
        logger.info(f"Classification complete: {result}")
        
        return result


# Global classifier instance
_classifier_instance = None


def get_classifier() -> LLMClassifier:
    """Get or create the global classifier instance (singleton pattern)"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = LLMClassifier()
    return _classifier_instance
