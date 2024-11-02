from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from fastapi import HTTPException
from time import sleep

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

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        sleep(2)  # Allow time for dynamic content to load
        content = driver.page_source
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Selenium error: {str(e)}")
    finally:
        driver.quit()
