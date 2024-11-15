import logging
import random
import asyncio
from fastapi import HTTPException
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from time import sleep
from .selenium_pool import driver_pool

logger = logging.getLogger(__name__)

async def get_with_selenium_async(url: str, task_id: str = None, max_retries: int = 3) -> str:
    """Fetches page content using Selenium WebDriver - asynchronous is used by websockets approach."""

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.error(f"Invalid URL: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL provided")

    for attempt in range(1, max_retries + 1):
        try:
            # Now passing task_id to acquire_driver
            async with driver_pool.acquire_driver(task_id) as driver:
                logger.info(f"Fetching URL: {url} (Attempt {attempt})")

                # Using asyncio.to_thread for potentially blocking Selenium operations
                def selenium_ops():
                    driver.get(url)
                    sleep(2)  # Allow initial page load
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    sleep(2)  # Wait for additional content
                    return driver.page_source

                content = await asyncio.to_thread(selenium_ops)
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

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if attempt == max_retries:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

        finally:
            logger.info(f"Completed attempt {attempt} for {url}")

    logger.error(f"Failed to retrieve content after {max_retries} attempts")
    raise HTTPException(status_code=500, detail="Failed to retrieve content after multiple attempts")

def get_with_selenium(url: str, max_retries: int = 3) -> str:
    """Fetches page content using Selenium for JavaScript-rendered content - synchronous approach is used by HTTP requests approach."""

    # Check URL validity
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.error(f"Invalid URL: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL provided")

    chrome_options = Options()
    # Disable options were added to avoid pop-ups, however they still don't work. 
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--log-level=3") 
    chrome_options.add_argument("--silent")

    # List of user-agent strings for simulating different browsers
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36"
    ]
    # Generate a random user-agent
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    chrome_options.add_argument("referer=https://www.google.com/")
    chrome_options.add_argument("accept-language=en-US,en;q=0.9")

    # Logging preferences for capturing performance logs
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    
    # Set up the Chrome driver service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Retry fetching the URL multiple times
    for attempt in range(1, max_retries + 1):
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(60)  # Timeout setting

            logger.info(f"Fetching URL: {url} (Attempt {attempt})")
            driver.get(url)
            sleep(2)  # Allow initial page load

            # Scroll to bottom to load dynamic content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)  # Wait for additional content

            content = driver.page_source
            return content

        except TimeoutException as e:
            logger.warning(f"Timeout while fetching {url}: {e}")
            if attempt == max_retries:
                raise HTTPException(status_code=504, detail="Timeout while loading the page")

        except WebDriverException as e:
            logger.error(f"Selenium WebDriver error: {e}")
            raise HTTPException(status_code=500, detail="Internal error with Selenium WebDriver")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

        finally:
            driver.quit()

    # If all attempts fail
    logger.error(f"Failed to retrieve content after {max_retries} attempts")
    raise HTTPException(status_code=500, detail="Failed to retrieve content after multiple attempts")