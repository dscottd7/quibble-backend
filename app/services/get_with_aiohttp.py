from fastapi import HTTPException
from fake_useragent import UserAgent
import aiohttp


async def get_with_aiohttp(url: str) -> str:
    """Try to fetch page with aiohttp first (faster)"""
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=30) as response:
            if response.status == 200:
                return await response.text()
            raise HTTPException(status_code=response.status, detail="Failed to fetch page")
