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
            
            # Check if debug mode (show browser window)
            import os
            headless_mode = os.getenv('HEADLESS', 'true').lower() == 'true'
            
            if not headless_mode:
                logger.info("🎬 LAUNCHING VISIBLE BROWSER (debug mode)")
            
            # Launch Chrome (not Chromium) with stealth and autoplay enabled
            # Use Chrome to get proprietary codec support (H.264, AAC, etc) needed for TikTok
            self.browser = await self.playwright.chromium.launch(
                headless=headless_mode,  # Can be disabled via HEADLESS=false in .env
                channel='chrome',  # Use Google Chrome instead of Chromium (has codecs!)
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--autoplay-policy=no-user-gesture-required',  # Allow autoplay without user gesture
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
                # Log important cookie names for debugging
                cookie_names = [c.get('name') for c in cookies]
                has_session = any('sessionid' in name.lower() or 'sid' in name.lower() for name in cookie_names)
                
                await self.context.add_cookies(cookies)
                logger.info(f"Injected {len(cookies)} cookies")
                logger.info(f"Cookie names: {', '.join(cookie_names[:10])}...")  # Show first 10
                
                if not has_session:
                    logger.warning("⚠️ No session cookies found (sessionid/sid) - login may fail!")
            else:
                logger.warning("⚠️ No cookies provided - will not be logged in!")
            
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
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            # Check if we're actually logged in
            is_logged_in = await self.page.evaluate("""
                () => {
                    // Check for login indicators (use valid browser JavaScript, not Playwright selectors)
                    const loginButton = document.querySelector('[data-e2e="top-login-button"]');
                    
                    // Check for user profile indicators
                    const hasUserAvatar = document.querySelector('[data-e2e="user-avatar"]') ||
                                         document.querySelector('[class*="Avatar"]');
                    
                    // If no login button found, we're probably logged in
                    // Or if we have user avatar, we're definitely logged in
                    return !loginButton || !!hasUserAvatar;
                }
            """)
            
            if not is_logged_in:
                logger.error("❌ NOT LOGGED IN TO TIKTOK!")
                logger.error("The cookies provided are either invalid or expired.")
                logger.error("Please make sure you:")
                logger.error("  1. Are logged in to TikTok in your browser")
                logger.error("  2. Have recent/valid cookies")
                logger.error("  3. Export cookies from the SAME browser session")
                raise RuntimeError("Not logged in to TikTok - cookies invalid or expired")
            
            logger.info("✅ Logged in to TikTok successfully")
            
            # Wait for video to load
            await self.page.wait_for_selector('video', timeout=10000)
            logger.info("✅ Video element found")
            
            # Wait for video source to actually load
            logger.info("Waiting for video source to load...")
            await asyncio.sleep(3)  # Give TikTok time to load video sources
            
            # CRITICAL: Click on the page and play the video to satisfy autoplay policies
            logger.info("Enabling autoplay by interacting with page...")
            try:
                await self._ensure_video_playing()
            except Exception as play_err:
                logger.warning(f"Video play attempt failed: {play_err}")
                # Don't fail session if video play fails, just continue
            
        except Exception as e:
            logger.error(f"Failed to navigate to FYP: {e}")
            # Don't close browser on navigation error
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
            # CHECK FOR CAPTCHA FIRST (before doing anything else)
            captcha_detected = await self._check_for_captcha()
            if captcha_detected:
                logger.warning("🤖 CAPTCHA DETECTED!")
                
                # Try to dismiss it by clicking X button
                logger.info("Attempting to dismiss captcha by clicking X button...")
                dismissed = await self._dismiss_captcha()
                
                if dismissed:
                    logger.info("✅ Captcha dismissed successfully!")
                    await asyncio.sleep(2)  # Let page stabilize
                    
                    # Check if another captcha appeared
                    still_captcha = await self._check_for_captcha()
                    if not still_captcha:
                        logger.info("✅ No more captchas, continuing...")
                    else:
                        logger.warning("⚠️ Captcha still present after dismiss, waiting for manual solve...")
                        captcha_solved = await self._wait_for_captcha_solve(timeout=60)
                        if not captcha_solved:
                            logger.error("❌ Captcha not solved in time - stopping session")
                            raise RuntimeError("Captcha not solved - TikTok blocked automation")
                        logger.info("✅ Captcha solved manually! Continuing...")
                else:
                    logger.warning("Could not auto-dismiss captcha, waiting for manual solve...")
                    logger.info("Since HEADLESS=false, you can solve it in the visible browser window")
                    
                    captcha_solved = await self._wait_for_captcha_solve(timeout=60)
                    if not captcha_solved:
                        logger.error("❌ Captcha not solved in time - stopping session")
                        raise RuntimeError("Captcha not solved - TikTok blocked automation")
                    
                    logger.info("✅ Captcha solved! Continuing...")
                
                await asyncio.sleep(2)  # Let page stabilize after captcha
            
            # Find active video (no wait - video is already ready from scroll)
            video = await self.page.query_selector('video')
            if not video:
                logger.warning("No video element found")
                return None
            
            # CRITICAL: Ensure video is playing before we capture screenshots
            await self._ensure_video_playing()
            
            # Start capturing screenshots immediately (video is ready)
            logger.info("Capturing screenshots while page stabilizes...")
            screenshot_task = asyncio.create_task(self._capture_screenshots(video))
            
            # Wait for page stabilization (for metadata elements)
            logger.info("Waiting for page stabilization...")
            await asyncio.sleep(1.0)
            
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
                        
                        // 🚨 CHECK FOR LIVE VIDEO (these break the flow)
                        const liveBadge = container.querySelector('[data-e2e="live-badge"]') ||
                                         container.querySelector('[class*="LiveTag"]') ||
                                         document.querySelector('[data-e2e="live-badge"]') ||
                                         document.querySelector('span[style*="LIVE"]');
                        
                        if (liveBadge) {
                            return { error: 'LIVE video detected - skipping' };
                        }
                        
                        // BETTER STRATEGY: Find any link to the video first
                        let videoUrl = '';
                        let username = '';
                        let videoId = '';
                        
                        // Strategy 1: Find direct video link (most reliable)
                        const allLinks = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                        let videoLink = null;
                        
                        for (const link of allLinks) {
                            const rect = link.getBoundingClientRect();
                            // Check if link is in the viewport area
                            if (rect.top >= -500 && rect.bottom <= window.innerHeight + 500) {
                                videoLink = link;
                                break;
                            }
                        }
                        
                        // If found link, extract URL, username, and ID from it
                        if (videoLink) {
                            videoUrl = videoLink.href;
                            const urlMatch = videoUrl.match(/\\/@([^/]+)\\/video\\/(\\d+)/);
                            if (urlMatch) {
                                username = urlMatch[1];
                                videoId = urlMatch[2];
                            }
                        }
                        
                        // Strategy 2: Extract from current URL (if on individual video page)
                        if (!videoUrl) {
                            const currentUrl = window.location.href;
                            const urlMatch = currentUrl.match(/\\/@([^/]+)\\/video\\/(\\d+)/);
                            if (urlMatch) {
                                videoUrl = currentUrl;
                                username = urlMatch[1];
                                videoId = urlMatch[2];
                            }
                        }
                        
                        // Strategy 3: Try to extract username separately
                        if (!username) {
                            const usernameEl = document.querySelector('[data-e2e="browse-username"]') ||
                                              document.querySelector('[data-e2e="video-author-uniqueid"]') ||
                                              container.querySelector('a[href^="/@"]') ||
                                              document.querySelector('a[href^="/@"]');
                            username = usernameEl?.textContent?.trim().replace('@', '') || '';
                            
                            // Try extracting from any /@username link
                            if (!username) {
                                const userLink = document.querySelector('a[href*="/@"]');
                                if (userLink) {
                                    const match = userLink.href.match(/\\/@([^/]+)/);
                                    username = match ? match[1] : '';
                                }
                            }
                        }
                        
                        // Fallback: Use FYP URL if we couldn't get the real video URL
                        if (!videoUrl) {
                            videoUrl = 'https://www.tiktok.com/foryou';
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
                        
                        return {
                            username: username || 'unknown',
                            videoUrl,
                            caption,
                            hashtags,
                            debug: {
                                foundContainer: !!container,
                                foundUsername: !!username,
                                foundVideoLink: !!videoLink,
                                videoCount: videos.length,
                                extractedVideoId: videoId || 'none',
                                extractionMethod: videoLink ? 'video-link' : 'url-parse'
                            }
                        };
                    } catch (err) {
                        return { error: err.toString() };
                    }
                }
            """)
            
            logger.info(f"JS evaluation result: {video_data}")
            
            if not video_data or video_data.get('error'):
                error_msg = video_data.get('error', 'Unknown error') if video_data else 'No data'
                
                # Special handling for LIVE videos
                if 'LIVE' in str(error_msg).upper():
                    logger.warning("🔴 LIVE video detected - using aggressive scroll to get past it")
                    # LIVE videos have different DOM structure, use multiple scroll attempts
                    await self._aggressive_scroll_past_live()
                else:
                    logger.error(f"Failed to extract: {error_msg}")
                
                return None
            
            # Remove debug info before returning
            if 'debug' in video_data:
                logger.info(f"Debug info: {video_data['debug']}")
                del video_data['debug']
            
            # Wait for screenshot task to complete (should be done by now)
            logger.info("Waiting for screenshots to finish...")
            screenshots = await screenshot_task
            
            if not screenshots:
                logger.error("Screenshot capture failed")
                return None
            
            # Store all screenshots for GPT analysis
            video_data['allScreenshots'] = screenshots  # All 3 frames will be sent to GPT
            
            logger.info(f"✅ Extracted video with {len(screenshots)} sequential frames: {video_data['videoUrl']}")
            self.stats['currentVideo'] = video_data['videoUrl']
            
            return video_data
            
        except Exception as e:
            logger.error(f"Failed to extract video data: {e}", exc_info=True)
            return None
    
    async def like_video(self):
        """Like the current video using EXACT selectors from TikTok's DOM"""
        if not self.page:
            return False
        
        try:
            logger.info("🔍 Looking for like button of the CURRENTLY VISIBLE video...")
            
            # CRITICAL: Find the like button for the VISIBLE video, not just any video
            # Multiple videos exist in DOM during scroll, so we need to scope to the visible one
            like_button_info = await self.page.evaluate("""
                () => {
                    // Step 1: Find the currently visible video
                    const videos = Array.from(document.querySelectorAll('video'));
                    let activeVideo = null;
                    
                    for (const vid of videos) {
                        const rect = vid.getBoundingClientRect();
                        // Video is visible if it's roughly in the center of viewport
                        const isInCenter = rect.top >= -100 && rect.top <= 300;
                        if (isInCenter) {
                            activeVideo = vid;
                            break;
                        }
                    }
                    
                    if (!activeVideo && videos.length > 0) {
                        activeVideo = videos[0];
                    }
                    
                    if (!activeVideo) {
                        return { found: false, reason: 'No video element found' };
                    }
                    
                    // Step 2: Find the article/container for this video
                    const article = activeVideo.closest('article');
                    if (!article) {
                        return { found: false, reason: 'No article container found' };
                    }
                    
                    // Step 3: Find the like button WITHIN this article
                    const likeButton = article.querySelector('button[aria-label^="Like video"]');
                    if (!likeButton) {
                        return { found: false, reason: 'Like button not found in article' };
                    }
                    
                    // Step 4: Check if already liked
                    const span = likeButton.querySelector('span[data-e2e="like-icon"]');
                    const color = span?.style.color || window.getComputedStyle(span).color;
                    const isLiked = color.includes('254') || color.includes('FE2C');
                    
                    // Step 5: Return a unique identifier we can use to click the RIGHT button
                    const ariaLabel = likeButton.getAttribute('aria-label');
                    
                    return {
                        found: true,
                        isLiked: isLiked,
                        ariaLabel: ariaLabel,
                        spanColor: color
                    };
                }
            """)
            
            if not like_button_info.get('found'):
                logger.warning(f"❌ {like_button_info.get('reason')}")
                return False
            
            if like_button_info.get('isLiked'):
                logger.info(f"ℹ️ Video already liked (color: {like_button_info.get('spanColor')})")
                return True
            
            logger.info(f"Found like button for visible video: {like_button_info.get('ariaLabel')[:30]}...")
            
            # Now we need to click using PLAYWRIGHT (not JavaScript) for proper events
            # Find the visible video's article and get the like button element
            articles = await self.page.query_selector_all('article')
            like_button_element = None
            
            for article in articles:
                # Check if this article has a video that's visible
                has_visible_video = await article.evaluate("""
                    (art) => {
                        const video = art.querySelector('video');
                        if (!video) return false;
                        
                        const rect = video.getBoundingClientRect();
                        const isInCenter = rect.top >= -100 && rect.top <= 300;
                        return isInCenter;
                    }
                """)
                
                if has_visible_video:
                    # This is the visible video's article, find its like button
                    like_button_element = await article.query_selector('button[aria-label^="Like video"]')
                    if like_button_element:
                        logger.info("Found like button element in visible article")
                        break
            
            if not like_button_element:
                logger.error("❌ Could not find like button element for visible video")
                return False
            
            # Get color before click
            color_before = await like_button_element.evaluate("""
                (btn) => {
                    const span = btn.querySelector('span[data-e2e="like-icon"]');
                    return span?.style.color || window.getComputedStyle(span).color;
                }
            """)
            
            # Click using Playwright's NATIVE click (generates ALL proper mouse events)
            logger.info(f"Clicking with Playwright native click (color before: {color_before})...")
            await like_button_element.click(delay=150)  # 150ms click delay like a human
            
            # Wait for TikTok's like animation and API call
            await asyncio.sleep(2.5)
            
            # Check color after
            color_after = await like_button_element.evaluate("""
                (btn) => {
                    const span = btn.querySelector('span[data-e2e="like-icon"]');
                    return span?.style.color || window.getComputedStyle(span).color;
                }
            """)
            
            aria_after = await like_button_element.get_attribute('aria-label')
            
            # Verify like worked
            is_liked = 'rgb(254, 44, 85)' in color_after or '254' in color_after.replace(' ', '')
            
            if is_liked:
                logger.info(f"✅ Video LIKED successfully! ❤️")
                logger.info(f"   Color: {color_before} → {color_after}")
                logger.info(f"   Aria: {aria_after}")
            else:
                logger.warning(f"⚠️ Like may have failed or is delayed")
                logger.warning(f"   Color before: {color_before}")
                logger.warning(f"   Color after: {color_after}")
                logger.warning(f"   Expected: rgb(254, 44, 85)")
                
                # Wait extra time and check again
                await asyncio.sleep(2.0)
                color_final = await like_button_element.evaluate("""
                    (btn) => {
                        const span = btn.querySelector('span[data-e2e="like-icon"]');
                        return span?.style.color || window.getComputedStyle(span).color;
                    }
                """)
                
                if 'rgb(254, 44, 85)' in color_final or '254' in color_final.replace(' ', ''):
                    logger.info(f"✅ Like succeeded after delay! Color: {color_final}")
                else:
                    logger.error(f"❌ Like failed - final color: {color_final}")
            
            await asyncio.sleep(0.5)
            return True
                
        except Exception as e:
            logger.error(f"Failed to like video: {e}")
            return False
    
    async def scroll_to_next_video(self):
        """Scroll to next video and wait for animation to complete"""
        if not self.page:
            return False
        
        try:
            logger.info("Scrolling to next video...")
            
            # Method 1: Arrow Down key
            await self.page.keyboard.press('ArrowDown')
            
            # Wait for scroll animation to START
            await asyncio.sleep(0.8)
            
            # Wait for scroll animation to COMPLETE
            # Check when video position stabilizes (not moving anymore)
            try:
                await self.page.wait_for_function(
                    """
                    () => {
                        const videos = document.querySelectorAll('video');
                        if (videos.length === 0) return false;
                        
                        // Find video in center of viewport (the active one)
                        for (const vid of videos) {
                            const rect = vid.getBoundingClientRect();
                            // Check if video is centered (scroll animation complete)
                            const isCentered = Math.abs(rect.top) < 50;  // Within 50px of top
                            if (isCentered && vid.readyState >= 2) {
                                return true;
                            }
                        }
                        return false;
                    }
                    """,
                    timeout=5000
                )
                logger.info("✅ Scroll animation completed, video centered")
            except Exception as e:
                logger.warning(f"Scroll animation timeout, continuing anyway: {e}")
                await asyncio.sleep(1.5)  # Extra wait if detection failed
            
            # CRITICAL: Ensure the video starts playing after scroll
            await self._ensure_video_playing()
            
            # Extra stabilization time to let all DOM updates complete
            await asyncio.sleep(0.5)
            
            logger.info("✅ Scrolled to next video and page stabilized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return False
    
    async def _aggressive_scroll_past_live(self):
        """
        Aggressively scroll past LIVE videos (they have sticky DOM that resists normal scrolling)
        
        LIVE videos often don't scroll properly with a single ArrowDown, so we:
        1. Press ArrowDown multiple times
        2. Use wheel events
        3. Direct scroll manipulation
        4. Wait longer for transition
        """
        logger.info("🔴 Using aggressive scroll to bypass LIVE video...")
        
        try:
            # Scroll attempt 1: Multiple ArrowDown presses
            for i in range(3):
                await self.page.keyboard.press('ArrowDown')
                await asyncio.sleep(0.3)
            
            # Scroll attempt 2: Wheel events
            for i in range(2):
                await self.page.evaluate('window.scrollBy({top: window.innerHeight, behavior: "smooth"})')
                await asyncio.sleep(0.3)
            
            # Scroll attempt 3: Direct page scroll
            await self.page.evaluate('window.scrollTo({top: window.scrollY + window.innerHeight * 2, behavior: "smooth"})')
            
            # Wait longer for LIVE video to transition away
            await asyncio.sleep(2)
            
            logger.info("✅ Aggressive scroll completed")
            
        except Exception as e:
            logger.error(f"Error during aggressive scroll: {e}")
    
    async def _check_for_captcha(self) -> bool:
        """
        Check if a captcha is present on the page
        
        Returns:
            True if captcha detected, False otherwise
        """
        if not self.page:
            return False
        
        try:
            captcha_detected = await self.page.evaluate("""
                () => {
                    // Check for common captcha indicators
                    const captchaSelectors = [
                        'div[id*="captcha"]',
                        'div[class*="captcha"]',
                        'div[class*="Captcha"]',
                        'iframe[src*="captcha"]',
                        'div[class*="verify"]',
                        'div[class*="Verify"]',
                        '[role="dialog"]',
                    ];
                    
                    // Use text content check (works in browser JS)
                    const bodyText = document.body.textContent || '';
                    if (bodyText.toLowerCase().includes('drag the slider') ||
                        bodyText.toLowerCase().includes('verify you are human') ||
                        bodyText.toLowerCase().includes('fit the puzzle')) {
                        return true;
                    }
                    
                    // Check for captcha elements
                    for (const selector of captchaSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.offsetParent !== null) {  // Visible
                            return true;
                        }
                    }
                    
                    return false;
                }
            """)
            
            return captcha_detected
            
        except Exception as e:
            logger.error(f"Error checking for captcha: {e}")
            return False
    
    async def _dismiss_captcha(self) -> bool:
        """
        Try to dismiss captcha by clicking the X button in the top right
        
        Returns:
            True if captcha was dismissed, False otherwise
        """
        if not self.page:
            return False
        
        try:
            logger.info("🔍 Looking for captcha close button (X)...")
            
            # Find and click the X button
            dismissed = await self.page.evaluate("""
                () => {
                    // Find modal/dialog (topmost element)
                    const modalSelectors = [
                        '[role="dialog"]',
                        'div[class*="Modal"]',
                        'div[class*="modal"]',
                        'div[id*="captcha"]',
                        'div[class*="verify"]'
                    ];
                    
                    let modal = null;
                    for (const selector of modalSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.offsetParent !== null) {
                            modal = el;
                            break;
                        }
                    }
                    
                    if (!modal) {
                        return { success: false, reason: 'No modal found' };
                    }
                    
                    // Find close button (X) in top right
                    const closeSelectors = [
                        'button[aria-label*="close" i]',
                        'button[aria-label*="Close" i]',
                        'button[class*="close"]',
                        'button[class*="Close"]',
                        'svg[class*="close"]',
                        'div[class*="close"]',
                        // Generic close button patterns
                        'button:has(svg)',  // Buttons with SVG (often close buttons)
                    ];
                    
                    let closeButton = null;
                    let usedSelector = null;
                    
                    // Search within the modal first
                    for (const selector of closeSelectors) {
                        if (selector.includes(':has')) continue;  // Skip Playwright-only selectors
                        
                        const btn = modal.querySelector(selector);
                        if (btn) {
                            // Check if it's in the top-right area
                            const rect = btn.getBoundingClientRect();
                            const modalRect = modal.getBoundingClientRect();
                            
                            // Top right = right side of modal and top area
                            const isTopRight = (rect.right > modalRect.right - 100) && 
                                              (rect.top < modalRect.top + 100);
                            
                            if (isTopRight || btn.textContent.includes('×') || btn.textContent.includes('✕')) {
                                closeButton = btn;
                                usedSelector = selector;
                                break;
                            }
                        }
                    }
                    
                    // Fallback: Find ANY button in top right of modal
                    if (!closeButton) {
                        const allButtons = modal.querySelectorAll('button');
                        for (const btn of allButtons) {
                            const rect = btn.getBoundingClientRect();
                            const modalRect = modal.getBoundingClientRect();
                            
                            const isTopRight = (rect.right > modalRect.right - 100) && 
                                              (rect.top < modalRect.top + 100);
                            
                            if (isTopRight) {
                                closeButton = btn;
                                usedSelector = 'top-right button';
                                break;
                            }
                        }
                    }
                    
                    if (!closeButton) {
                        return { success: false, reason: 'Close button not found' };
                    }
                    
                    // Click the close button
                    closeButton.click();
                    
                    return {
                        success: true,
                        selector: usedSelector
                    };
                }
            """)
            
            if dismissed.get('success'):
                logger.info(f"✅ Clicked captcha close button: {dismissed.get('selector')}")
                await asyncio.sleep(1)  # Wait for modal to close
                return True
            else:
                logger.warning(f"⚠️ Could not dismiss captcha: {dismissed.get('reason')}")
                return False
            
        except Exception as e:
            logger.error(f"Error dismissing captcha: {e}")
            return False
    
    async def _wait_for_captcha_solve(self, timeout: int = 60) -> bool:
        """
        Wait for captcha to be solved (by human in visible browser)
        
        Args:
            timeout: Max seconds to wait
            
        Returns:
            True if captcha solved, False if timeout
        """
        logger.info(f"⏳ Waiting up to {timeout} seconds for captcha to be solved...")
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            # Check if captcha still present
            captcha_still_there = await self._check_for_captcha()
            
            if not captcha_still_there:
                return True
            
            await asyncio.sleep(5)  # Check every 5 seconds
            logger.info(f"⏳ Still waiting for captcha solve... ({int(asyncio.get_event_loop().time() - start_time)}s elapsed)")
        
        return False
    
    async def _ensure_video_playing(self):
        """
        Ensure video is playing by clicking on video element and explicitly playing video.
        This is critical for satisfying browser autoplay policies.
        
        Key fixes:
        - Videos MUST be muted for autoplay to work (browser policy)
        - Wait for video to be ready before playing
        - Retry with muted video if unmuted fails
        - Dismiss any error overlays
        - Click on VIDEO element specifically to avoid hitting like buttons
        """
        if not self.page or not self.is_running:
            return
        
        try:
            # Strategy 1: Click on the VIDEO element specifically (not center of viewport)
            # This avoids accidentally clicking like buttons during scroll transitions
            logger.info("Clicking on video element to enable autoplay...")
            await self.page.evaluate("""
                () => {
                    // Find the active video
                    const videos = Array.from(document.querySelectorAll('video'));
                    let activeVideo = null;
                    
                    for (const vid of videos) {
                        const rect = vid.getBoundingClientRect();
                        const isVisible = rect.top >= -200 && rect.bottom <= window.innerHeight + 200;
                        if (isVisible) {
                            activeVideo = vid;
                            break;
                        }
                    }
                    
                    if (!activeVideo && videos.length > 0) {
                        activeVideo = videos[0];
                    }
                    
                    if (activeVideo) {
                        // Click directly on the video element (not on buttons)
                        const rect = activeVideo.getBoundingClientRect();
                        const event = new MouseEvent('click', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: rect.left + rect.width / 2,
                            clientY: rect.top + rect.height / 2
                        });
                        activeVideo.dispatchEvent(event);
                    }
                }
            """)
            await asyncio.sleep(0.3)
            
            # Strategy 2: Explicitly play the video element (with retry logic)
            logger.info("Explicitly playing video...")
            play_result = await self.page.evaluate("""
                async () => {
                    const videos = Array.from(document.querySelectorAll('video'));
                    if (videos.length === 0) {
                        return { success: false, error: 'No video found' };
                    }
                    
                    // Find visible video
                    let activeVideo = null;
                    for (const vid of videos) {
                        const rect = vid.getBoundingClientRect();
                        const isVisible = rect.top >= -200 && rect.bottom <= window.innerHeight + 200;
                        if (isVisible) {
                            activeVideo = vid;
                            break;
                        }
                    }
                    
                    if (!activeVideo) {
                        activeVideo = videos[0];
                    }
                    
                    // Wait for video to have a source loaded (readyState >= 1 means HAVE_METADATA)
                    // If readyState is 0, the video hasn't loaded any data yet
                    let waitCount = 0;
                    while (activeVideo.readyState === 0 && waitCount < 30) {
                        await new Promise(resolve => setTimeout(resolve, 200));
                        waitCount++;
                    }
                    
                    if (activeVideo.readyState === 0) {
                        return {
                            success: false,
                            error: 'Video source never loaded (readyState still 0)',
                            readyState: 0
                        };
                    }
                    
                    // Now wait for video to be ready to play (readyState >= 2 means HAVE_CURRENT_DATA)
                    waitCount = 0;
                    while (activeVideo.readyState < 2 && waitCount < 15) {
                        await new Promise(resolve => setTimeout(resolve, 200));
                        waitCount++;
                    }
                    
                    // CRITICAL: Videos MUST be muted for autoplay to work (browser policy)
                    activeVideo.muted = true;
                    
                    try {
                        await activeVideo.play();
                        return { 
                            success: true, 
                            playing: !activeVideo.paused,
                            readyState: activeVideo.readyState,
                            muted: activeVideo.muted
                        };
                    } catch (err) {
                        // If play fails, try again after a short delay
                        await new Promise(resolve => setTimeout(resolve, 500));
                        try {
                            await activeVideo.play();
                            return { 
                                success: true, 
                                playing: !activeVideo.paused,
                                readyState: activeVideo.readyState,
                                muted: activeVideo.muted,
                                retriedOnce: true
                            };
                        } catch (retryErr) {
                            return { 
                                success: false, 
                                error: retryErr.toString(),
                                playing: !activeVideo.paused,
                                readyState: activeVideo.readyState
                            };
                        }
                    }
                }
            """)
            
            if play_result.get('success'):
                logger.info(f"✅ Video playing: {play_result.get('playing')} (muted: {play_result.get('muted')}, readyState: {play_result.get('readyState')})")
                if play_result.get('retriedOnce'):
                    logger.info("  (succeeded on retry)")
            else:
                logger.warning(f"⚠️ Video play attempt failed: {play_result.get('error', 'Unknown error')}")
                logger.warning(f"  readyState: {play_result.get('readyState')}, playing: {play_result.get('playing')}")
            
            # Strategy 3: Dismiss any error overlays (e.g., "video currently not able to play")
            await self.page.evaluate("""
                () => {
                    // Look for and dismiss error messages/overlays
                    const errorSelectors = [
                        '[data-e2e="video-error"]',
                        '[class*="error"]',
                        '[class*="Error"]',
                        'div[role="dialog"]'
                    ];
                    
                    for (const selector of errorSelectors) {
                        const errorEls = document.querySelectorAll(selector);
                        errorEls.forEach(el => {
                            if (el.textContent.toLowerCase().includes('not able to play') ||
                                el.textContent.toLowerCase().includes('error')) {
                                // Try to find and click dismiss button
                                const closeBtn = el.querySelector('button') || 
                                                el.querySelector('[role="button"]');
                                if (closeBtn) closeBtn.click();
                                // Or just hide it
                                el.style.display = 'none';
                            }
                        });
                    }
                }
            """)
            
            # Give video time to start
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error ensuring video plays: {e}")
    
    async def stop(self):
        """Stop the browser and cleanup - handles errors gracefully"""
        self.is_running = False
        self.stats['status'] = 'stopped'
        
        # Close each component individually with error handling
        if self.page:
            try:
                await self.page.close()
            except Exception as e:
                logger.warning(f"Error closing page: {e}")
            finally:
                self.page = None
        
        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
            finally:
                self.context = None
        
        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.browser = None
        
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
            finally:
                self.playwright = None
        
        logger.info("✅ Browser stopped and cleaned up")
    
    async def _capture_screenshots(self, video) -> List[str]:
        """
        Capture 3 sequential screenshots of the video
        
        Args:
            video: Playwright video element handle
            
        Returns:
            List of base64-encoded screenshot data URLs
        """
        try:
            screenshots = []
            num_frames = 3
            quality = 50  # Good quality for GPT vision analysis
            
            for i in range(num_frames):
                try:
                    # Try video element screenshot first
                    screenshot_bytes = await video.screenshot(type='jpeg', quality=quality)
                except Exception as video_err:
                    # If video element screenshot fails, fallback to full page screenshot
                    logger.warning(f"Video screenshot failed, using page screenshot: {video_err}")
                    try:
                        screenshot_bytes = await self.page.screenshot(type='jpeg', quality=quality)
                    except Exception as page_err:
                        logger.error(f"Page screenshot also failed: {page_err}")
                        # Skip this frame but continue to next
                        continue
                
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                screenshots.append(f"data:image/jpeg;base64,{screenshot_base64}")
                logger.info(f"Captured frame {i+1}/{num_frames}")
                
                # 1 second delay between captures
                if i < num_frames - 1:
                    await asyncio.sleep(1.0)
            
            # Return what we got (even if not all 3 frames)
            if len(screenshots) == 0:
                logger.error("Failed to capture any screenshots")
                return []
            
            logger.info(f"Successfully captured {len(screenshots)}/{num_frames} frames")
            return screenshots
            
        except Exception as e:
            logger.error(f"Error capturing screenshots: {e}")
            return []
    
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

