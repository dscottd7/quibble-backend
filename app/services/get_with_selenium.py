import logging
import asyncio
from fastapi import HTTPException
from selenium.common.exceptions import WebDriverException, TimeoutException
from urllib.parse import urlparse
from .selenium_pool import driver_pool

logger = logging.getLogger(__name__)


async def get_with_selenium(url: str, max_retries: int = 3) -> str:
    """Fetches page content using Selenium with proper resource management"""

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.error(f"Invalid URL: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL provided")

    for attempt in range(1, max_retries + 1):
        try:
            async with driver_pool.acquire_driver() as driver:
                logger.info(f"Fetching URL: {url} (Attempt {attempt})")
                
                async def safe_selenium_ops():
                    try:
                        # Execute Selenium operations directly
                        driver.get(url)
                        await asyncio.sleep(2)  # Allow initial page load
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        await asyncio.sleep(2)  # Wait for additional content
                        return driver.page_source
                    except Exception as e:
                        logger.error(f"Error in Selenium operations: {e}")
                        raise

                # Run the Selenium operations
                content = await safe_selenium_ops()
                
                if not content:
                    raise ValueError("No content retrieved from page")
                    
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

        except ValueError as e:
            logger.error(f"Value error: {e}")
            if attempt == max_retries:
                raise HTTPException(status_code=500, detail=str(e))

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if attempt == max_retries:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
            
        finally:
            logger.info(f"Completed attempt {attempt} for {url}")

    logger.error(f"Failed to retrieve content after {max_retries} attempts")
    raise HTTPException(status_code=500, detail="Failed to retrieve content after multiple attempts")