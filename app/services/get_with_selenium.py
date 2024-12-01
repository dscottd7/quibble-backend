from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse
import asyncio
import logging
import random
from time import sleep
from fastapi import HTTPException
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
