# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from contextlib import asynccontextmanager
# import asyncio
# import logging
# from typing import AsyncGenerator, Dict, List
# import random
# from typing import Dict, List

# logger = logging.getLogger(__name__)


# class WebDriverPool:
#     def __init__(self, max_drivers: int = 4):
#         self.max_drivers = max_drivers
#         self._semaphore = asyncio.Semaphore(max_drivers)
#         self._init_lock = asyncio.Lock()
#         self._initialized = False
#         self._driver_service = None
#         self._active_drivers: Dict[str, List[webdriver.Chrome]] = {}
#         self._retry_delay = 1.0

#     async def init(self):
#         """Initialize the WebDriver service once"""
#         async with self._init_lock:
#             if not self._initialized:
#                 try:
#                     self._driver_service = Service(ChromeDriverManager().install())
#                     self._initialized = True
#                 except Exception as e:
#                     logger.error(f"Failed to initialize WebDriver service: {e}")
#                     raise

#     def _create_chrome_options(self) -> Options:
#         """Create Chrome options with enhanced anti-detection measures"""
#         options = Options()
        
#         # Basic options
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-gpu')
#         options.add_argument('--disable-dev-shm-usage')
#         options.add_argument('--disable-infobars')
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument('--disable-extensions')
#         options.add_argument('--no-first-run')
#         options.add_argument('--no-default-browser-check')
#         options.add_argument('--no-service-autorun')
#         options.add_argument('--password-store=basic')
#         options.add_argument('--disable-notifications')
#         options.add_argument('--headless=new')
#         options.add_argument('--disable-blink-features=AutomationControlled')
#         options.add_experimental_option('excludeSwitches', ['enable-automation'])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument('--start-maximized')
        
#         # Random viewport
#         viewports = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900)]
#         viewport = random.choice(viewports)
#         options.add_argument(f'--window-size={viewport[0]},{viewport[1]}')
        
#         # Random user agent
#         USER_AGENTS = [
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
#         ]
#         options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
        
#         # Language and headers
#         LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-CA,en;q=0.9"]
#         options.add_argument(f'--lang={random.choice(LANGUAGES)}')
#         options.add_argument(f'--accept-language={random.choice(LANGUAGES)}')
#         options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        
#         # Set legitimate referrer
#         options.add_argument('--referrer=https://www.google.com/')

#         # Unique debugging port to prevent conflicts
#         debug_port = random.randint(9222, 9999)
#         options.add_argument(f'--remote-debugging-port={debug_port}')

#         return options

#     async def _create_driver_with_retry(self, max_retries: int = 2) -> webdriver.Chrome:
#         """Create a WebDriver with retry logic"""
#         last_exception = None

#         for attempt in range(max_retries):
#             try:
#                 driver = webdriver.Chrome(
#                     service=self._driver_service,
#                     options=self._create_chrome_options()
#                 )
#                 driver.set_page_load_timeout(30)
#                 return driver
#             except Exception as e:
#                 last_exception = e
#                 logger.warning(f"Failed to create driver (attempt {attempt + 1}/{max_retries}): {e}")
#                 if attempt < max_retries - 1:
#                     await asyncio.sleep(self._retry_delay * (attempt + 1))

#         raise last_exception

#     @asynccontextmanager
#     async def acquire_driver(self, task_id: str) -> AsyncGenerator[webdriver.Chrome, None]:
#         """Acquire a WebDriver instance from the pool"""
#         await self.init()

#         async with self._semaphore:
#             driver = None
#             try:
#                 driver = await self._create_driver_with_retry()
#                 if task_id not in self._active_drivers:
#                     self._active_drivers[task_id] = []
#                 self._active_drivers[task_id].append(driver)
#                 yield driver
#             finally:
#                 if driver:
#                     try:
#                         await asyncio.sleep(3)
#                         driver.quit()
#                         await asyncio.sleep(1)
#                         if task_id in self._active_drivers:
#                             self._active_drivers[task_id].remove(driver)
#                             if not self._active_drivers[task_id]:
#                                 del self._active_drivers[task_id]
#                     except Exception as e:
#                         logger.error(f"Error closing WebDriver: {e}")

#     def cleanup_for_task(self, task_id: str):
#         """Cleanup all drivers associated with a task"""
#         if task_id in self._active_drivers:
#             drivers = self._active_drivers[task_id]
#             for driver in drivers:
#                 try:
#                     driver.quit()
#                 except Exception as e:
#                     logger.error(f"Error closing driver during cleanup: {e}")
#             del self._active_drivers[task_id]


# # Create a global instance of the WebDriver pool
# driver_pool = WebDriverPool(max_drivers=2)

# # Export the driver_pool instance
# __all__ = ['driver_pool']
