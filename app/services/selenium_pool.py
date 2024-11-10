from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import AsyncGenerator
import random

logger = logging.getLogger(__name__)


class WebDriverPool:
    def __init__(self, max_drivers: int = 2):
        self.max_drivers = max_drivers
        self._semaphore = asyncio.Semaphore(max_drivers)
        self._init_lock = asyncio.Lock()
        self._initialized = False
        self._driver_service = None

    async def init(self):
        """Initialize the WebDriver service once"""
        async with self._init_lock:
            if not self._initialized:
                try:
                    self._driver_service = Service(ChromeDriverManager().install())
                    self._initialized = True
                except Exception as e:
                    logger.error(f"Failed to initialize WebDriver service: {e}")
                    raise

    def _create_chrome_options(self) -> Options:
        """Create Chrome options with randomized user agent"""
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Security and performance options
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--no-default-browser-check")
        
        # Debugging and logging
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        
        # Headers and identity
        chrome_options.add_argument("referer=https://www.google.com/")
        chrome_options.add_argument("accept-language=en-US,en;q=0.9")

        # Performance options
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Set performance logging preferences
        chrome_options.set_capability(
            "goog:loggingPrefs", 
            {"performance": "ALL", "browser": "ALL"}
        )

        # User agents
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36"
        ]
        chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
        
        return chrome_options

    @asynccontextmanager
    async def acquire_driver(self) -> AsyncGenerator[webdriver.Chrome, None]:
        """Acquire a WebDriver instance from the pool"""
        await self.init()  # Ensure service is initialized
        
        async with self._semaphore:
            driver = None
            try:
                # Create driver without deprecated desired_capabilities
                driver = webdriver.Chrome(
                    service=self._driver_service,
                    options=self._create_chrome_options()
                )
                driver.set_page_load_timeout(30)
                
                # Set window size for consistency
                driver.set_window_size(1920, 1080)
                
                yield driver
                
            except Exception as e:
                logger.error(f"Error creating WebDriver: {e}")
                raise
                
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception as e:
                        logger.error(f"Error closing WebDriver: {e}")


# Create a global instance of the WebDriver pool
driver_pool = WebDriverPool(max_drivers=2)
