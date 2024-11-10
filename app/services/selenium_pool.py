from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import asynccontextmanager
import asyncio
import logging
from typing import AsyncGenerator
import random
from typing import Dict, List

logger = logging.getLogger(__name__)


class WebDriverPool:
    def __init__(self, max_drivers: int = 2):
        self.max_drivers = max_drivers
        self._semaphore = asyncio.Semaphore(max_drivers)
        self._init_lock = asyncio.Lock()
        self._initialized = False
        self._driver_service = None
        self._active_drivers: Dict[str, List[webdriver.Chrome]] = {}
        self._retry_delay = 1.0  # Delay between retries in seconds

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
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
        ]
        chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
        return chrome_options

    async def _create_driver_with_retry(self, max_retries: int = 3) -> webdriver.Chrome:
        """Create a WebDriver with retry logic"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                driver = webdriver.Chrome(
                    service=self._driver_service,
                    options=self._create_chrome_options()
                )
                driver.set_page_load_timeout(30)
                return driver
            except Exception as e:
                last_exception = e
                logger.warning(f"Failed to create driver (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))  # Exponential backoff
        
        raise last_exception

    @asynccontextmanager
    async def acquire_driver(self, task_id: str) -> AsyncGenerator[webdriver.Chrome, None]:
        """Acquire a WebDriver instance from the pool"""
        await self.init()
        
        async with self._semaphore:
            driver = None
            try:
                driver = await self._create_driver_with_retry()
                
                # Track the driver for this task
                if task_id not in self._active_drivers:
                    self._active_drivers[task_id] = []
                self._active_drivers[task_id].append(driver)
                
                yield driver
            finally:
                if driver:
                    try:
                        driver.quit()
                        await asyncio.sleep(0.5)
                        
                        # Remove from tracking
                        if task_id in self._active_drivers:
                            self._active_drivers[task_id].remove(driver)
                            if not self._active_drivers[task_id]:
                                del self._active_drivers[task_id]
                    except Exception as e:
                        logger.error(f"Error closing WebDriver: {e}")

    def cleanup_for_task(self, task_id: str):
        """Cleanup all drivers associated with a task"""
        if task_id in self._active_drivers:
            drivers = self._active_drivers[task_id]
            for driver in drivers:
                try:
                    driver.quit()
                except Exception as e:
                    logger.error(f"Error closing driver during cleanup: {e}")
            del self._active_drivers[task_id]


# Create a global instance of the WebDriver pool
driver_pool = WebDriverPool(max_drivers=2)
