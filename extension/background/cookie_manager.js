/**
 * Cookie Manager
 * Extracts TikTok cookies for backend session authentication
 */

/**
 * Get all TikTok cookies from the user's browser
 * @returns {Promise<Array>} Array of cookie objects
 */
async function getTikTokCookies() {
  try {
    const cookies = await chrome.cookies.getAll({
      domain: '.tiktok.com'
    });
    
    console.log('[Cookie Manager] Found', cookies.length, 'TikTok cookies');
    
    // Convert to format expected by Playwright
    const playwrightCookies = cookies.map(cookie => ({
      name: cookie.name,
      value: cookie.value,
      domain: cookie.domain,
      path: cookie.path,
      expires: cookie.expirationDate || -1,
      httpOnly: cookie.httpOnly || false,
      secure: cookie.secure || false,
      sameSite: cookie.sameSite || 'Lax'
    }));
    
    return playwrightCookies;
  } catch (error) {
    console.error('[Cookie Manager] Error getting cookies:', error);
    return [];
  }
}

/**
 * Get user agent string
 * @returns {string} User agent
 */
function getUserAgent() {
  return navigator.userAgent;
}

/**
 * Validate that we have essential TikTok cookies
 * @param {Array} cookies - Array of cookie objects
 * @returns {boolean} True if essential cookies are present
 */
function validateTikTokCookies(cookies) {
  // Check for essential TikTok session cookies
  const essentialCookies = ['sessionid', 'tt_webid', 'tt_webid_v2'];
  const cookieNames = cookies.map(c => c.name);
  
  for (const essential of essentialCookies) {
    if (!cookieNames.includes(essential)) {
      console.warn(`[Cookie Manager] Missing essential cookie: ${essential}`);
    }
  }
  
  // At minimum, we need tt_webid
  return cookieNames.includes('tt_webid') || cookieNames.includes('tt_webid_v2');
}

// Export functions
export { getTikTokCookies, getUserAgent, validateTikTokCookies };

