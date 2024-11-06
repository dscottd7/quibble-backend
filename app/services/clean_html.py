from fastapi import HTTPException
from bs4 import BeautifulSoup
from typing import Optional
import logging

# Get logger for the current module
logger = logging.getLogger(__name__)


class SelectorNotFoundError(Exception):
    """Custom exception for missing CSS selector in HTML."""
    pass


def clean_html(html_content: str, selector: Optional[str] = None) -> str:
    """Extract text content from HTML, optionally using a CSS selector."""
    if not html_content:
        logger.error("Empty HTML content received")
        raise ValueError("HTML content cannot be empty")

    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for tag in soup(["script", "style", "meta", "link"]):
        tag.decompose()

    if selector:
        try:
            elements = soup.select(selector)
            if not elements:
                raise SelectorNotFoundError(f"Selector '{selector}' not found in the provided HTML content.")
            return " ".join(element.get_text(strip=True, separator=" ") for element in elements)
        except SelectorNotFoundError as e:
            logger.warning(f"Selector warning: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error when using selector '{selector}': {e}")
            raise HTTPException(status_code=500, detail="An error occurred while applying the selector.")

    # Get text from all remaining elements
    try:
        content = soup.get_text(separator=" ").strip()
    except Exception as e:
        logger.error(f"Unexpected error extracting text from HTML content: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while extracting text from HTML content.")

    # Remove extra whitespace characters
    return content.replace('\n', '').replace('\r', '').replace('\t', '')