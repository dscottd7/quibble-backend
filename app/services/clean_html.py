from fastapi import HTTPException
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from typing import Optional


def clean_html(html_content: str, selector: Optional[str] = None) -> str:
    """Extract text content from HTML, optionally using a CSS selector"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style", "meta", "link"]):
        script.decompose()

    if selector:
        elements = soup.select(selector)
        if not elements:
            raise HTTPException(status_code=404, detail=f"Selector '{selector}' not found")
        return "\n".join(element.get_text(strip=True, separator=" ") for element in elements)

    # Get text from all remaining elements
    return soup.get_text(separator=" ").strip()