"""
Playwright-based TikTok automation bot
Handles headless browser automation with stealth mode and session injection
"""

import asyncio
import logging
import base64
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from PIL import Image
import io

logger = logging.getLogger(__name__)


class TikTokBot:
    """Headless browser automation for TikTok FYP calibration"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_running = False
        self.stats = {
            'videosProcessed': 0,
            'matchesFound': 0,
            'matchRate': 0.0,
            'status': 'idle',
            'currentVideo': None
        }
        
    async def start(self, cookies: List[Dict], user_agent: str = None):
        """
        Start the headless browser with user's session
        
        Args:
            cookies: List of cookie dicts from user's browser
            user_agent: Optional user agent string
        """
        try:
            logger.info("Starting Playwright browser...")
            
            # Launch Playwright
            self.playwright = await async_playwright().start()
            
            # Launch Chromium in headless mode with stealth
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # Create context with user agent
            context_options = {
                'viewport': {'width': 1280, 'height': 720},
                'user_agent': user_agent or 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'locale': 'en-US',
                'timezone_id': 'America/New_York'
            }
            
            self.context = await self.browser.new_context(**context_options)
            
            # Inject cookies
            if cookies:
                await self.context.add_cookies(cookies)
                logger.info(f"Injected {len(cookies)} cookies")
            
            # Stealth modifications
            await self.context.add_init_script("""
                // Override navigator.webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override chrome property
                window.chrome = {
                    runtime: {}
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set extra headers
            await self.page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            })
            
            self.is_running = True
            self.stats['status'] = 'ready'
            logger.info("✅ Playwright browser ready!")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")
            await self.stop()
            raise
    
    async def navigate_to_fyp(self):
        """Navigate to TikTok For You Page"""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        try:
            logger.info("Navigating to TikTok FYP...")
            await self.page.goto('https://www.tiktok.com/foryou', wait_until='networkidle', timeout=30000)
            
            # Wait for video to load
            await self.page.wait_for_selector('video', timeout=10000)
            logger.info("✅ Loaded TikTok FYP")
            
            # Random delay to appear human
            await asyncio.sleep(2 + (asyncio.get_event_loop().time() % 1))
            
        except Exception as e:
            logger.error(f"Failed to navigate to FYP: {e}")
            raise
    
    async def get_current_video_data(self) -> Optional[Dict]:
        """
        Extract metadata from currently visible video
        
        Returns:
            dict with caption, hashtags, username, videoUrl, screenshot
        """
        if not self.page:
            return None
        
        try:
            # Wait a bit for page to stabilize
            await asyncio.sleep(1)
            
            # Find active video
            video = await self.page.query_selector('video')
            if not video:
                logger.warning("No video element found")
                return None
            
            # DEBUG: Log page structure
            page_info = await self.page.evaluate("""
                () => {
                    return {
                        url: window.location.href,
                        videoCount: document.querySelectorAll('video').length,
                        hasRecommendList: !!document.querySelector('[data-e2e="recommend-list-item"]'),
                        hasVideoContainer: !!document.querySelector('div[class*="VideoContainer"]'),
                        bodyClasses: document.body.className
                    };
                }
            """)
            logger.info(f"Page structure: {page_info}")
            
            # Extract metadata using JavaScript with extensive fallbacks
            video_data = await self.page.evaluate("""
                () => {
                    try {
                        // Find active video container (multiple strategies)
                        const videos = Array.from(document.querySelectorAll('video'));
                        if (videos.length === 0) return { error: 'No videos found' };
                        
                        let activeVideo = null;
                        
                        // Strategy 1: Find visible/playing video
                        for (const vid of videos) {
                            const rect = vid.getBoundingClientRect();
                            const isVisible = rect.top >= -200 && rect.bottom <= window.innerHeight + 200;
                            if ((isVisible && !vid.paused) || isVisible) {
                                activeVideo = vid;
                                break;
                            }
                        }
                        
                        // Strategy 2: Just take first video if none found
                        if (!activeVideo) {
                            activeVideo = videos[0];
                        }
                        
                        if (!activeVideo) return { error: 'No active video' };
                        
                        // Get container (multiple fallback strategies)
                        let container = activeVideo.closest('[data-e2e="recommend-list-item"]') ||
                                       activeVideo.closest('div[class*="DivVideoContainer"]') ||
                                       activeVideo.closest('div[class*="ItemContainer"]') ||
                                       activeVideo.parentElement?.parentElement?.parentElement;
                        
                        // If no container, use whole document
                        if (!container) {
                            container = document.body;
                        }
                        
                        // Extract username (multiple selectors)
                        const usernameEl = document.querySelector('[data-e2e="browse-username"]') ||
                                          document.querySelector('[data-e2e="video-author-uniqueid"]') ||
                                          container.querySelector('a[href^="/@"]') ||
                                          document.querySelector('a[href^="/@"]');
                        let username = usernameEl?.textContent?.trim().replace('@', '') || '';
                        
                        // Try to get from URL as fallback
                        if (!username) {
                            const urlMatch = window.location.href.match(/\\/@([^/]+)/);
                            username = urlMatch ? urlMatch[1] : '';
                        }
                        
                        // Extract video ID (multiple strategies)
                        const videoLink = container.querySelector('a[href*="/video/"]') ||
                                         document.querySelector('a[href*="/video/"]');
                        let videoId = videoLink?.href.match(/\\/video\\/(\\d+)/)?.[1] || '';
                        
                        // Try from URL
                        if (!videoId) {
                            const urlMatch = window.location.href.match(/\\/video\\/(\\d+)/);
                            videoId = urlMatch ? urlMatch[1] : '';
                        }
                        
                        // Extract caption (multiple selectors)
                        const captionEl = container.querySelector('[data-e2e="browse-video-desc"]') ||
                                         container.querySelector('[data-e2e="video-desc"]') ||
                                         container.querySelector('[class*="DivContainer"] span') ||
                                         document.querySelector('[data-e2e="browse-video-desc"]');
                        const caption = captionEl?.textContent?.trim() || '';
                        
                        // Extract hashtags
                        const hashtagEls = container.querySelectorAll('a[href*="/tag/"]');
                        const hashtags = Array.from(hashtagEls).map(el => 
                            el.textContent.replace('#', '').trim()
                        ).filter(Boolean);
                        
                        // Construct video URL
                        const videoUrl = username && videoId ? 
                            `https://www.tiktok.com/@${username}/video/${videoId}` : 
                            window.location.href;
                        
                        return {
                            username: username || 'unknown',
                            videoUrl,
                            caption,
                            hashtags,
                            debug: {
                                foundContainer: !!container,
                                foundUsername: !!usernameEl,
                                foundVideoLink: !!videoLink,
                                videoCount: videos.length
                            }
                        };
                    } catch (err) {
                        return { error: err.toString() };
                    }
                }
            """)
            
            logger.info(f"JS evaluation result: {video_data}")
            
            if not video_data or video_data.get('error'):
                logger.error(f"Failed to extract: {video_data}")
                return None
            
            # Remove debug info before returning
            if 'debug' in video_data:
                logger.info(f"Debug info: {video_data['debug']}")
                del video_data['debug']
            
            # Validate we have minimal data
            if not video_data.get('username') or video_data['username'] == 'unknown':
                logger.warning("Could not identify username, skipping video")
                return None
            
            # Capture screenshot
            screenshot_bytes = await video.screenshot(type='jpeg', quality=60)
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            video_data['screenshot'] = f"data:image/jpeg;base64,{screenshot_base64}"
            
            logger.info(f"✅ Extracted video: {video_data['videoUrl']}")
            self.stats['currentVideo'] = video_data['videoUrl']
            
            return video_data
            
        except Exception as e:
            logger.error(f"Failed to extract video data: {e}", exc_info=True)
            return None
    
    async def like_video(self):
        """Like the current video"""
        if not self.page:
            return False
        
        try:
            # Find like button
            like_button = await self.page.query_selector(
                '[data-e2e="browse-like"], [data-e2e="like-icon"], button[aria-label*="like"]'
            )
            
            if like_button:
                # Check if already liked
                is_liked = await like_button.evaluate(
                    'el => el.classList.contains("liked") || el.getAttribute("aria-pressed") === "true"'
                )
                
                if not is_liked:
                    await like_button.click()
                    logger.info("✅ Liked video")
                    await asyncio.sleep(0.5 + (asyncio.get_event_loop().time() % 0.5))
                    return True
                else:
                    logger.info("Video already liked")
                    return True
            else:
                logger.warning("Like button not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to like video: {e}")
            return False
    
    async def scroll_to_next_video(self):
        """Scroll to next video"""
        if not self.page:
            return False
        
        try:
            logger.info("Scrolling to next video...")
            
            # Method 1: Arrow Down key
            await self.page.keyboard.press('ArrowDown')
            await asyncio.sleep(1)
            
            # Method 2: Wheel event (backup)
            await self.page.evaluate('window.scrollBy({top: window.innerHeight, behavior: "smooth"})')
            
            # Wait for new video to load
            await asyncio.sleep(2 + (asyncio.get_event_loop().time() % 1))
            
            logger.info("✅ Scrolled to next video")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return False
    
    async def stop(self):
        """Stop the browser and cleanup"""
        self.is_running = False
        self.stats['status'] = 'stopped'
        
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("✅ Browser stopped and cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_stats(self) -> Dict:
        """Get current stats"""
        return self.stats.copy()
    
    def update_stats(self, is_match: bool):
        """Update statistics after processing a video"""
        self.stats['videosProcessed'] += 1
        if is_match:
            self.stats['matchesFound'] += 1
        
        if self.stats['videosProcessed'] > 0:
            self.stats['matchRate'] = self.stats['matchesFound'] / self.stats['videosProcessed']


# Global bot instance
_bot_instance: Optional[TikTokBot] = None


def get_bot() -> TikTokBot:
    """Get or create the global bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TikTokBot()
    return _bot_instance

