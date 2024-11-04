import asyncio
import logging
from fastapi import APIRouter, HTTPException
from app.models.url_request import URLRequest
from app.models.user_input import UserInput
from app.models.selected_categories import SelectedCategories
from app.services.prompt_service import create_prompt
from app.services.openai_service import call_openai_api
from app.models.scrape_request import ScrapeRequest
from app.services.get_with_selenium import get_with_selenium
from app.services.clean_html import clean_html

# Initialize the router
router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_and_clean(url: str):
    """Helper function to fetch and clean HTML content with exception handling."""
    try:
        html_content = await asyncio.get_event_loop().run_in_executor(None, get_with_selenium, url)
        return clean_html(html_content)
    except Exception as e:
        logger.error(f"Error fetching content for {url}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching URL content")


@router.post("/compare")
async def compare_urls(urls: URLRequest, user_input: UserInput):
    """ API route to handle POST request for product comparson """
    try:
        # Validate selected categories
        try:
            SelectedCategories.validate_categories(user_input.selected_categories)
        except ValueError as e:
            logger.warning(f"Invalid categories: {user_input.selected_categories} - {e}")
            raise HTTPException(status_code=400, detail="Invalid selected categories")

        # Fetch and clean HTML content for each URL
        parsed_url1_html = await fetch_and_clean(str(urls.url1))
        parsed_url2_html = await fetch_and_clean(str(urls.url2))

        # Generate the prompt for OpenAI API
        try:
            prompt = create_prompt(parsed_url1_html, parsed_url2_html, user_input.selected_categories, user_input.user_preference)
        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            raise HTTPException(status_code=500, detail="Error creating prompt")

        # Call OpenAI API for comparison
        try:
            openai_response = call_openai_api(prompt)
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise HTTPException(status_code=502, detail="Error calling OpenAI API")

        return {"comparison": openai_response}

    except HTTPException as e:
        # Allow raised HTTPExceptions to propagate
        raise e
    except Exception as e:
        # Handle unexpected errors
        logger.critical(f"Unexpected error in /compare route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/scrape")
def scrape_url(request: ScrapeRequest):
    """ Experimental route to handle scraping for user agent blocking and JS rendering """
    try:
        # Using selenium to render page and express any JavaScript
        content = get_with_selenium(str(request.url))
        return {"text": clean_html(content)}
    except Exception as e:
        logger.error(f"Error scraping URL {request.url}: {e}")
        raise HTTPException(status_code=500, detail="Error scraping the URL")


@router.post("/openai-test")
async def test_openai(urls: URLRequest):
    """ Created a route to test OpenAi itegration independently. 
    This should be modified. Current function is not working """
    try:
        # Generate a simple prompt
        prompt = f"Compare the following two products:\n\nProduct 1: \n{urls.url1}\n\nProduct 2:\n{urls.url2}"

        # Call OpenAI API to get comparison results
        try:
            openai_response = call_openai_api(prompt)
            return {"comparison": openai_response.get("choices")[0].get("text")}
        except Exception as e:
            logger.error(f"OpenAI test API call failed: {e}")
            raise HTTPException(status_code=502, detail="OpenAI API call failed")

    except Exception as e:
        logger.critical(f"Unexpected error in /openai-test route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
