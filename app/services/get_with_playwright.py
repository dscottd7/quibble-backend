from fastapi import HTTPException
from fake_useragent import UserAgent
from playwright.async_api import async_playwright


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
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
        })

        try:
            await page.goto(url, wait_until='networkidle')
            content = await page.content()
            await browser.close()
            return content
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Playwright error: {str(e)}")
