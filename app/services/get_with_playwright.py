from fastapi import HTTPException
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
import asyncio


async def get_with_playwright(url: str) -> str:
    """Fallback to playwright for JavaScript-rendered content"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=UserAgent().random,
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Referer': 'https://www.google.com/'  # Simulate coming from a search engine
        })

        try:
            await page.goto(url, wait_until='networkidle')
            await asyncio.sleep(2)  # Add delay to allow dynamic content to load
            content = await page.content()
            await browser.close()
            return content
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Playwright error: {str(e)}")
