"""
Session management for TikTok calibration automation
Orchestrates the Playwright bot and classification pipeline
"""

import asyncio
import logging
from typing import Optional, Dict, Callable
from .playwright_bot import get_bot, TikTokBot
from classifier.llm_classifier import get_classifier

logger = logging.getLogger(__name__)


class CalibrationSession:
    """Manages a single calibration session"""
    
    def __init__(
        self,
        session_id: str,
        category: str,
        category_description: str,
        cookies: list,
        user_agent: str,
        stats_callback: Optional[Callable] = None
    ):
        self.session_id = session_id
        self.category = category
        self.category_description = category_description
        self.cookies = cookies
        self.user_agent = user_agent
        self.stats_callback = stats_callback
        
        self.bot: TikTokBot = get_bot()
        self.classifier = get_classifier()
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the calibration session"""
        if self.is_running:
            logger.warning(f"Session {self.session_id} already running")
            return
        
        logger.info(f"Starting calibration session: {self.session_id}")
        logger.info(f"Category: {self.category}")
        logger.info(f"Description: {self.category_description}")
        
        try:
            # Start browser with user's cookies
            await self.bot.start(self.cookies, self.user_agent)
            
            # Navigate to FYP
            await self.bot.navigate_to_fyp()
            
            # Start calibration loop
            self.is_running = True
            self.task = asyncio.create_task(self._calibration_loop())
            
            logger.info(f"✅ Session {self.session_id} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start session {self.session_id}: {e}")
            await self.stop()
            raise
    
    async def _calibration_loop(self):
        """Main calibration loop - only calls GPT after successful scroll"""
        try:
            while self.is_running:
                # Get current video data
                video_data = await self.bot.get_current_video_data()
                
                if not video_data:
                    logger.warning("Failed to extract video data, scrolling to next...")
                    
                    # Send stats update even when skipping (keeps UI responsive)
                    if self.stats_callback:
                        stats = self.bot.get_stats()
                        await self.stats_callback(stats)
                    
                    await self.bot.scroll_to_next_video()
                    await asyncio.sleep(2)  # Reduced from 4s to 2s
                    continue
                
                # Update current video in stats (ALWAYS update this)
                self.bot.stats['currentVideo'] = video_data.get('videoUrl', 'N/A')
                
                # Send stats update to keep UI in sync
                if self.stats_callback:
                    logger.info(f"📊 Sending stats update: {self.bot.get_stats()}")
                    await self.stats_callback(self.bot.get_stats())
                else:
                    logger.warning("⚠️ No stats_callback set - UI will not update!")
                
                logger.info(f"Processing: {video_data['videoUrl']}")
                
                # Classify video with GPT (only called when we have valid video data)
                # No try/catch here - if classification fails, the session should stop
                # Get all screenshots for multi-frame analysis
                import base64
                all_screenshots = video_data.get('allScreenshots', [])
                
                # Decode first screenshot as fallback single image (for backwards compatibility)
                if all_screenshots:
                    screenshot_data = all_screenshots[0].split(',')[1] if ',' in all_screenshots[0] else all_screenshots[0]
                    screenshot_bytes = base64.b64decode(screenshot_data)
                else:
                    screenshot_bytes = b''
                
                # Classify with LLM (send all screenshots)
                classification = await self.classifier.classify(
                    image=screenshot_bytes,
                    caption=video_data.get('caption', ''),
                    hashtags=video_data.get('hashtags', []),
                    username=video_data.get('username', ''),
                    category=self.category,
                    category_description=self.category_description,
                    all_screenshots=all_screenshots
                )
                
                confidence = classification.get('confidence', 0.0)
                reasoning = classification.get('reasoning', '')
                
                # Determine match based on confidence threshold (0.5 = 50%)
                CONFIDENCE_THRESHOLD = 0.5
                is_match = confidence >= CONFIDENCE_THRESHOLD
                
                logger.info(f"Classification: confidence={confidence:.2f} (threshold={CONFIDENCE_THRESHOLD})")
                logger.info(f"Reasoning: {reasoning}")
                
                # Update stats
                self.bot.update_stats(is_match)
                
                # Execute action based on classification
                if is_match:
                    logger.info(f"✅ MATCH! (confidence {confidence:.2f} >= {CONFIDENCE_THRESHOLD}) Liking video...")
                    await self.bot.like_video()
                    await asyncio.sleep(1)  # Short delay after liking
                else:
                    logger.info(f"❌ No match (confidence {confidence:.2f} < {CONFIDENCE_THRESHOLD}), skipping...")
                
                # Send stats update via callback
                if self.stats_callback:
                    stats = self.bot.get_stats()
                    stats['lastClassification'] = {
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'videoUrl': video_data['videoUrl'],
                        'isMatch': is_match  # Keep for frontend compatibility
                    }
                    await self.stats_callback(stats)
                
                # Scroll to next video (after classification is done)
                logger.info("Scrolling to next video...")
                await self.bot.scroll_to_next_video()
                
                # Wait for scroll to complete and new video to load (reduced for speed)
                await asyncio.sleep(1.5)  # Reduced from 3s to 1.5s
                
                # Check completion
                stats = self.bot.get_stats()
                if self._should_complete(stats):
                    logger.info("🎉 Calibration complete!")
                    await self.stop()
                    break
                
        except asyncio.CancelledError:
            logger.info(f"Session {self.session_id} cancelled")
        except Exception as e:
            logger.error(f"Calibration loop error: {e}")
            await self.stop()
    
    def _should_complete(self, stats: Dict) -> bool:
        """Check if calibration is complete"""
        # Need at least 20 videos
        if stats['videosProcessed'] < 20:
            return False
        
        # Target: 70% match rate
        if stats['matchRate'] >= 0.70:
            logger.info(f"Target match rate achieved: {stats['matchRate']:.1%}")
            return True
        
        # Safety: max 100 videos
        if stats['videosProcessed'] >= 100:
            logger.info(f"Max videos reached: {stats['videosProcessed']}")
            return True
        
        return False
    
    async def stop(self):
        """Stop the calibration session"""
        logger.info(f"Stopping session {self.session_id}")
        self.is_running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        await self.bot.stop()
        logger.info(f"✅ Session {self.session_id} stopped")
    
    def get_status(self) -> Dict:
        """Get current session status"""
        return {
            'session_id': self.session_id,
            'is_running': self.is_running,
            'category': self.category,
            'stats': self.bot.get_stats()
        }


# Global session registry
_active_sessions: Dict[str, CalibrationSession] = {}


def get_session(session_id: str) -> Optional[CalibrationSession]:
    """Get an active session by ID"""
    return _active_sessions.get(session_id)


def create_session(
    session_id: str,
    category: str,
    category_description: str,
    cookies: list,
    user_agent: str,
    stats_callback: Optional[Callable] = None
) -> CalibrationSession:
    """Create a new calibration session"""
    if session_id in _active_sessions:
        raise ValueError(f"Session {session_id} already exists")
    
    session = CalibrationSession(
        session_id,
        category,
        category_description,
        cookies,
        user_agent,
        stats_callback
    )
    _active_sessions[session_id] = session
    return session


async def stop_session(session_id: str):
    """Stop and remove a session - always removes from registry even if stop fails"""
    session = _active_sessions.pop(session_id, None)
    if session:
        try:
            await session.stop()
        except Exception as e:
            logger.error(f"Error stopping session {session_id}: {e}")
            # Still remove from registry even if stop failed
            pass


def list_sessions() -> list:
    """List all active session IDs"""
    return list(_active_sessions.keys())

