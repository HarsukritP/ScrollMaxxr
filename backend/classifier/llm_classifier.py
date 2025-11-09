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

Your task: Determine if this video matches what the user wants to see.

Return ONLY a JSON object in this exact format:
{{"isMatch": true, "confidence": 0.85, "reasoning": "brief explanation"}}

or

{{"isMatch": false, "confidence": 0.3, "reasoning": "brief explanation"}}

Be strict in classification. If unsure or borderline, use isMatch: false and confidence < 0.5.
Focus on both visual elements in the screenshot AND text content (caption, hashtags)."""


class LLMClassifier:
    """
    Multimodal LLM classifier for TikTok content using OpenAI GPT-5-nano.
    """
    
    def __init__(self):
        """Initialize the classifier with OpenAI client"""
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        logger.info("OpenAI GPT-5-nano classifier initialized")
    
    async def classify(
        self,
        image: bytes,
        caption: str,
        hashtags: List[str],
        username: str,
        category: str,
        category_description: str,
        video_url: str = None,
        transcript: str = None
    ) -> dict:
        """
        Classify video content using OpenAI GPT-5-nano.
        
        Args:
            image: Video screenshot as bytes
            caption: Video caption text
            hashtags: List of hashtags
            username: Video author username
            category: Selected category name or "Custom"
            category_description: Description of desired content
            video_url: Optional TikTok video URL for transcript fetching
            transcript: Optional pre-fetched transcript
        
        Returns:
            dict with isMatch, category, confidence, reasoning
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
            
            # Try OpenAI classification
            try:
                result = await self._classify_with_openai(
                    image, caption, hashtags, username, desired_content, category, transcript
                )
                return result
            except Exception as e:
                logger.warning(f"OpenAI classification failed: {e}")
                # Fallback to rule-based
                logger.warning("Falling back to rule-based classification")
                return self._rule_based_classify(caption, hashtags, category, category_description)
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            # Return a safe fallback result
            return {
                'isMatch': False,
                'category': category,
                'confidence': 0.0,
                'reasoning': f'Classification failed: {str(e)}'
            }
    
    async def _classify_with_openai(
        self,
        image: bytes,
        caption: str,
        hashtags: List[str],
        username: str,
        desired_content: str,
        category: str,
        transcript: str = None
    ) -> dict:
        """Classify using OpenAI GPT-5-nano"""
        
        # Build system prompt
        system_prompt = SYSTEM_PROMPT.format(desired_content=desired_content)
        
        # Build user prompt with metadata
        user_prompt = f"""Caption: {caption}
Hashtags: {', '.join(hashtags) if hashtags else 'None'}
Username: @{username}"""
        
        # Add transcript if available
        if transcript:
            user_prompt += f"\nVideo Transcript: {transcript[:500]}"  # Limit to 500 chars to save tokens
        
        user_prompt += "\n\nAnalyze the image and text above. Does this video match what the user wants to see?\nReturn JSON only (no other text)."
        
        # Encode image to base64
        image_base64 = base64.b64encode(image).decode('utf-8')
        
        # Validate we have real image data (not a tiny placeholder)
        if len(image) < 1000:
            logger.warning("Image data is suspiciously small, may be invalid")
            # Fall back to text-only classification
            return self._rule_based_classify(caption, hashtags, category, category_description)
        
        logger.info("Sending request to OpenAI GPT-5-nano...")
        
        # Call OpenAI API with vision
        response = client.chat.completions.create(
            model="gpt-5-nano-2025-08-07",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "low"  # Use low detail for faster processing
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=300,  # GPT-5-nano uses max_completion_tokens instead of max_tokens
            temperature=0.3  # Lower temperature for more consistent results
        )
        
        logger.info("OpenAI response received")
        
        # Parse response
        result_text = response.choices[0].message.content.strip()
        logger.info(f"Raw response: {result_text[:200]}")
        
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
            logger.error(f"Response text: {result_text}")
            # Try to extract boolean from text
            is_match = 'true' in result_text.lower() or '"ismatch": true' in result_text.lower()
            result = {
                'isMatch': is_match,
                'confidence': 0.5,
                'reasoning': 'Failed to parse structured response'
            }
        
        # Ensure isMatch is boolean
        if isinstance(result.get('isMatch'), str):
            result['isMatch'] = result['isMatch'].lower() == 'true'
        
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
    
    def _rule_based_classify(
        self,
        caption: str,
        hashtags: List[str],
        category: str,
        category_description: str
    ) -> dict:
        """
        Simple keyword-based classification as fallback.
        """
        logger.info("Using rule-based classification")
        
        # Combine caption and hashtags
        text = (caption + ' ' + ' '.join(hashtags)).lower()
        
        # Extract keywords from description
        if category == "Custom":
            keywords = category_description.lower().split()
        else:
            keywords = CATEGORIES.get(category, category_description).lower().split()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
        
        # Count keyword matches
        match_score = sum(1 for keyword in keywords if keyword in text)
        
        # Calculate confidence
        confidence = min(match_score / max(len(keywords) / 2, 1), 1.0)
        
        # Simple threshold: need at least 2 keyword matches or 30% confidence
        is_match = match_score >= 2 or confidence >= 0.3
        
        result = {
            'isMatch': is_match,
            'category': category,
            'confidence': confidence,
            'reasoning': f'Keyword matching: {match_score}/{len(keywords)} keywords found (fallback method)'
        }
        
        logger.info(f"Rule-based result: {result}")
        
        return result
