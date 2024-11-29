from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import asyncio
import logging
import random
from time import sleep
import traceback
from fastapi import HTTPException
from .selenium_pool import driver_pool
import undetected_chromedriver as uc
import time


logger = logging.getLogger(__name__)


def random_sleep():
    """Add random delay to simulate human behavior"""
    sleep(random.uniform(1, 2))


def validate_url(url: str):
    """Validate the URL format"""
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.error(f"Invalid URL: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL provided")


async def get_with_selenium_async(url: str, task_id: str = None, max_retries: int = 2) -> str:
    """Fetches page content using a dedicated WebDriver instance per request."""
    validate_url(url)

    for attempt in range(1, max_retries + 1):
        driver = None
        try:
            # Create options for request
            options = Options()
            
            # Assign unique debugging port
            debug_port = random.randint(9222, 9999)
            options.add_argument(f'--remote-debugging-port={debug_port}')
            
            # Basic options
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-infobars')
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument('--disable-extensions')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')
            options.add_argument('--disable-notifications')
            options.add_argument('--headless=new')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--start-maximized')

            # Random user agent
            USER_AGENTS = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            ]
            options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
            
            # Language and headers
            LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-CA,en;q=0.9"]
            options.add_argument(f'--lang={random.choice(LANGUAGES)}')
            options.add_argument(f'--accept-language={random.choice(LANGUAGES)}')
            options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            
            # Set legitimate referrer
            options.add_argument('--referrer=https://www.google.com/')
            
            # Create WebDriver instance
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            def selenium_ops():
                try:
                    # Set timeouts
                    driver.set_page_load_timeout(30)
                    driver.implicitly_wait(10)
                    
                    # Visit Google first
                    driver.get('https://www.google.com')
                    time.sleep(random.uniform(1, 2))
                    
                    # Navigate to target URL
                    driver.get(url)
                    
                    # Wait for page to be interactive
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                    
                    # Get the initial viewport height and total height
                    viewport_and_total_height = driver.execute_script("""
                        return {
                            viewport: window.innerHeight,
                            total: Math.max(
                                document.body.scrollHeight,
                                document.documentElement.scrollHeight,
                                document.body.offsetHeight,
                                document.documentElement.offsetHeight
                            )
                        }
                    """)
                    
                    viewport_height = viewport_and_total_height['viewport']
                    total_height = viewport_and_total_height['total']
                    
                    # Perform human-like behavior with safety checks
                    if total_height > viewport_height:
                        # Set scroll positions
                        scroll_positions = [
                            int(total_height * ratio) 
                            for ratio in [0.3, 0.6, 0.9]
                        ]
                        
                        for scroll_pos in scroll_positions:
                            driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                            time.sleep(random.uniform(0.5, 1))
                    
                    # Scroll back to top
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(0.5)
                    
                    # Get the content after human simulation
                    content = driver.page_source
                    
                    if not content:
                        raise ValueError("Empty content received from page")
                        
                    return content
                    
                except Exception as e:
                    logger.error(f"Error in selenium_ops: {e}")
                    raise

            # Execute operations with timeout
            content = await asyncio.wait_for(
                asyncio.to_thread(selenium_ops),
                timeout=45
            )
            
            logger.info(f"Successfully retrieved content for {url} (length: {len(content)})")
            return content

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            if attempt == max_retries:
                raise HTTPException(
                    status_code=500,
                    detail=f"Operation failed: {str(e)}"
                )
            await asyncio.sleep(2 ** attempt)
            
        finally:
            # Clean up driver
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing driver: {e}")

    return None


def get_with_selenium(url: str, max_retries: int = 2) -> str:
    """Fetches page content using undetected-chromedriver to bypass bot detection."""
    
    logger.info(f"Starting scrape for URL: {url}")
    
    # Validate URL
    validate_url(url)

    # Browser configurations
    viewports = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900)]
    
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    ]

    LANGUAGES = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "en-CA,en;q=0.9"
    ]

    last_error = None
    last_traceback = None
    
    for attempt in range(1, max_retries + 1):
        driver = None
        try:
            logger.info(f"Attempt {attempt} of {max_retries}")
            
            # Create new ChromeOptions for each attempt
            options = uc.ChromeOptions()
            
            # Enhanced anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-infobars')
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument('--disable-extensions')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')
            options.add_argument('--disable-notifications')
            
            # Random configurations
            viewport = random.choice(viewports)
            options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
            options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
            options.add_argument(f'--lang={random.choice(LANGUAGES)}')
            
            # Add custom headers
            options.add_argument(f'--accept-language={random.choice(LANGUAGES)}')
            options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            
            # Set legitimate referrer
            options.add_argument('--referrer=https://www.google.com/')
            
            logger.info("Initializing Chrome driver...")
            driver = uc.Chrome(
                options=options,
                version_main=130,
                headless=True
            )
            
            # Set additional preferences
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(USER_AGENTS),
                "platform": random.choice(["Windows", "Macintosh", "Linux"])
            })
            
            # Set cookies to appear more legitimate
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Network.setCookie', {
                'domain': '.altrarunning.com',
                'name': 'visitor',
                'value': f'visitor_{random.randint(1000000, 9999999)}'
            })
            
            logger.info("Setting page load timeout...")
            driver.set_page_load_timeout(30)
            
            # Initial navigation to Google first
            logger.info("Navigating to Google first...")
            driver.get('https://www.google.com')
            random_sleep()
            
            # Now navigate to the target URL
            logger.info(f"Navigating to URL: {url}")
            driver.get(url)
            
            # Random delay after page load
            random_sleep()
            
            logger.info("Simulating human interaction...")
            # Simulate mouse movement
            driver.execute_script("""
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': Math.random() * window.innerWidth,
                    'clientY': Math.random() * window.innerHeight
                });
                document.dispatchEvent(event);
            """)
            
            # Random scrolling
            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            for i in range(3):
                scroll_height = random.randint(100, total_height)
                driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                random_sleep()
            
            logger.info("Getting page source...")
            content = driver.page_source
            
            if not content:
                raise ValueError("Empty content received from page")
            
            # Check for specific bot detection phrases
            if any(phrase in content.lower() for phrase in [
                "access to this page has been denied",
                "please verify you are a human",
                "please enable javascript",
                "detected unusual traffic",
                "automated access",
                "bot detected",
                "perimeterx"
            ]):
                raise HTTPException(status_code=403, detail="Bot detection triggered")
            
            logger.info("Successfully retrieved content")
            return content

        except Exception as e:
            last_error = e
            last_traceback = traceback.format_exc()
            logger.error(f"Error during attempt {attempt}: {str(e)}")
            logger.error(f"Traceback: {last_traceback}")
            
            if attempt == max_retries:
                error_message = f"Failed after {max_retries} attempts. Last error: {str(last_error)}\nTraceback: {last_traceback}"
                logger.error(error_message)
                raise HTTPException(status_code=500, detail=error_message)
            
            # Wait longer between retries
            sleep(random.uniform(5, 10))

        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Chrome driver closed successfully")
                except Exception as e:
                    logger.warning(f"Error closing driver: {e}")

    return None  # Should never reach here due to the exception in the try block
