from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from fastapi import HTTPException
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random


def get_with_selenium(url: str) -> str:
    """Fetches page content using Selenium for JavaScript-rendered content"""

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

    # Add headers and referrer
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    chrome_options.add_argument("referer=https://www.google.com/")
    chrome_options.add_argument("accept-language=en-US,en;q=0.9")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        sleep(3)  # Allow time for dynamic content to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to bottom of page
        sleep(3)
        content = driver.page_source
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Selenium error: {str(e)}")
    finally:
        driver.quit()
