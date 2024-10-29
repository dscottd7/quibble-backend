from fastapi import HTTPException
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright


def get_with_playwright(url: str) -> str:
    """Fallback to playwright for JavaScript-rendered content"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=UserAgent().random,
            viewport={'width': 1920, 'height': 1080}
        )

        page = context.new_page()
        page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
        })

        try:
            page.goto(url, wait_until='networkidle')
            content = page.content()
            return content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Playwright error: {str(e)}")
        finally:
            browser.close()
