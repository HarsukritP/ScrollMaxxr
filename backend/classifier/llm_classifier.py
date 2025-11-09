"""
LLM Classifier for TikTok Content
Uses Gemini Flash 1.5 for multimodal video classification with fallback options.
"""

import google.generativeai as genai
import os
from PIL import Image
import io
import json
from typing import List
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

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
Focus on both visual elements in the screenshot AND text content (caption, hashtags).
"""


class LLMClassifier:
    """
    Multimodal LLM classifier for TikTok content.
    Uses Gemini Flash 1.5 as primary, with fallback options.
    """
    
    def __init__(self):
        """Initialize the classifier with Gemini model"""
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✅ Gemini Flash 1.5 model initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini model: {e}")
            self.model = None
        
        # Check for fallback API keys
        self.has_openai = bool(os.getenv('OPENAI_API_KEY'))
        self.has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
        
        if self.has_openai:
            logger.info("✅ OpenAI API key found (fallback available)")
        if self.has_anthropic:
            logger.info("✅ Anthropic API key found (fallback available)")
    
    async def classify(
        self,
        image: bytes,
        caption: str,
        hashtags: List[str],
        username: str,
        category: str,
        category_description: str
    ) -> dict:
        """
        Classify video content using Gemini.
        
        Args:
            image: Video screenshot as bytes
            caption: Video caption text
            hashtags: List of hashtags
            username: Video author username
            category: Selected category name or "Custom"
            category_description: Description of desired content
        
        Returns:
            dict with isMatch, category, confidence, reasoning
        """
        try:
            # Determine desired content description
            if category == "Custom":
                desired_content = category_description
            else:
                # Use preset category description
                desired_content = f"{category}: {CATEGORIES.get(category, category_description)}"
            
            logger.info(f"🎯 Classifying for: {desired_content}")
            
            # Try Gemini first
            if self.model:
                try:
                    result = await self._classify_with_gemini(
                        image, caption, hashtags, username, desired_content, category
                    )
                    return result
                except Exception as e:
                    logger.warning(f"⚠️ Gemini classification failed: {e}")
            
            # Fallback to rule-based if Gemini fails
            logger.warning("⚠️ Falling back to rule-based classification")
            return self._rule_based_classify(caption, hashtags, category, category_description)
            
        except Exception as e:
            logger.error(f"❌ Classification error: {e}")
            # Return a safe fallback result
            return {
                'isMatch': False,
                'category': category,
                'confidence': 0.0,
                'reasoning': f'Classification failed: {str(e)}'
            }
    
    async def _classify_with_gemini(
        self,
        image: bytes,
        caption: str,
        hashtags: List[str],
        username: str,
        desired_content: str,
        category: str
    ) -> dict:
        """Classify using Gemini Flash 1.5"""
        
        # Build system prompt
        system_prompt = SYSTEM_PROMPT.format(desired_content=desired_content)
        
        # Build user prompt with metadata
        user_prompt = f"""
Caption: {caption}
Hashtags: {', '.join(hashtags) if hashtags else 'None'}
Username: @{username}

Analyze the image and text above. Does this video match what the user wants to see?
Return JSON only (no other text).
"""
        
        # Load image
        img = Image.open(io.BytesIO(image))
        logger.info(f"📸 Image loaded: {img.size} {img.format}")
        
        # Generate classification
        response = self.model.generate_content([
            system_prompt,
            user_prompt,
            img
        ])
        
        logger.info(f"🤖 Gemini response received")
        
        # Parse response
        result_text = response.text.strip()
        logger.info(f"📝 Raw response: {result_text[:200]}")
        
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
            is_match = 'true' in result_text.lower() or 'match' in result_text.lower()
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
        
        logger.info(f"✅ Classification: {result}")
        
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
        logger.info("🔄 Using rule-based classification")
        
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
        
        logger.info(f"✅ Rule-based result: {result}")
        
        return result

