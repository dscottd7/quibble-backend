from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
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


logger = logging.getLogger(__name__)


def random_sleep():
    """Add random delay to simulate human behavior"""
    sleep(random.uniform(1, 3))


def validate_url(url: str):
    """Validate the URL format"""
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.error(f"Invalid URL: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL provided")


async def get_with_selenium_async(url: str, task_id: str = None, max_retries: int = 2) -> str:
    """Fetches page content using Selenium WebDriver - asynchronous is used by websockets approach."""

    # Validate URL
    validate_url(url)

    for attempt in range(1, max_retries + 1):
        try:
            async with driver_pool.acquire_driver(task_id) as driver:
                logger.info(f"Fetching URL: {url} (Attempt {attempt})")
                
                # Using asyncio.to_thread for potentially blocking Selenium operations
                def selenium_ops():
                    try:
                        # Initial navigation to Google
                        driver.get('https://www.google.com')
                        random_sleep()
                        
                        # Set cookies to appear more legitimate
                        driver.execute_cdp_cmd('Network.enable', {})
                        driver.execute_cdp_cmd('Network.setCookie', {
                            'domain': urlparse(url).netloc,
                            'name': 'visitor',
                            'value': f'visitor_{random.randint(1000000, 9999999)}'
                        })
                        
                        # Navigate to target URL
                        driver.get(url)
                        random_sleep()
                        
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
                        
                        # Natural scrolling behavior
                        total_height = int(driver.execute_script("return document.body.scrollHeight"))
                        for i in range(3):
                            scroll_height = random.randint(100, total_height)
                            driver.execute_script(f"window.scrollTo(0, {scroll_height});")
                            random_sleep()
                        
                        # Wait for body to be present
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Get the content
                        content = driver.page_source
                        
                        # Check for bot detection
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
                        
                        return content
                        
                    except Exception as e:
                        logger.error(f"Error in selenium_ops: {e}")
                        raise

                content = await asyncio.to_thread(selenium_ops)
                
                if not content:
                    raise ValueError("Empty content received from page")
                
                logger.info(f"Successfully retrieved content for {url} (length: {len(content)})")
                return content

        except TimeoutException as e:
            logger.warning(f"Timeout while fetching {url}: {e}")
            if attempt == max_retries:
                raise HTTPException(status_code=504, detail="Timeout while loading the page")

        except WebDriverException as e:
            logger.error(f"Selenium WebDriver error: {e}")
            if attempt == max_retries:
                raise HTTPException(status_code=500, detail="Error with web driver")

        except HTTPException as e:
            # Re-raise HTTP exceptions immediately
            raise e

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            if attempt == max_retries:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

        finally:
            logger.info(f"Completed attempt {attempt} for {url}")
            await asyncio.sleep(random.uniform(3, 6))  # Wait between retries

    logger.error(f"Failed to retrieve content after {max_retries} attempts")
    raise HTTPException(status_code=500, detail="Failed to retrieve content after multiple attempts")


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
