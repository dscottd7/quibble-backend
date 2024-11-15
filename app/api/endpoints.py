import asyncio
import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import json
from app.models.url_request import URLRequest
from app.models.user_input import UserInput
from app.models.selected_categories import SelectedCategories
from app.models.comparison_manager import ComparisonManager
from app.services.prompt_service import create_prompt
from app.services.openai_service import call_openai_api
from app.models.scrape_request import ScrapeRequest
from app.services.get_with_selenium import get_with_selenium
from app.services.clean_html import clean_html
from app.services.structured_openai_service import call_openai_api_structured
import os

router = APIRouter()
logger = logging.getLogger(__name__)


# Initialize the comparison manager
comparison_manager = ComparisonManager()


@router.websocket("/ws/compare")
async def websocket_compare(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        # Receive the initial request data
        raw_data = await websocket.receive_json()

        # Debug log the received data
        logger.info("Received WebSocket data:")
        logger.info(f"Raw data: {raw_data}")

        if not isinstance(raw_data, dict):
            await comparison_manager.send_status(
                websocket,
                "error",
                "Invalid request format"
            )
            return

        urls = {
            'url1': raw_data['urls']['url1'].strip(),
            'url2': raw_data['urls']['url2'].strip()
        }
        user_input = raw_data.get('user_input')

        # Debug log the extracted URLs
        logger.info(f"Extracted URLs: {urls}")

        if not urls or not user_input:
            await comparison_manager.send_status(
                websocket,
                "error",
                "Missing required fields in request"
            )
            return

        # Start the comparison process
        await comparison_manager.start_comparison(websocket, urls, user_input)

    except WebSocketDisconnect:
        logger.info("Client disconnected")
        await comparison_manager.handle_client_disconnect(websocket)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        await comparison_manager.send_status(
            websocket,
            "error",
            "Invalid JSON format"
        )
    except Exception as e:
        logger.error(f"Error in websocket endpoint: {e}")
        await comparison_manager.send_status(
            websocket,
            "error",
            str(e)
        )

@router.websocket("/ws/compare/structured")
async def websocket_structured_compare(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        # Receive the initial request data
        raw_data = await websocket.receive_json()

        # Debug log the received data
        logger.info("Received WebSocket data:")
        logger.info(f"Raw data: {raw_data}")

        if not isinstance(raw_data, dict):
            await comparison_manager.send_status(
                websocket,
                "error",
                "Invalid request format"
            )
            return

        urls = {
            'url1': raw_data['urls']['url1'].strip(),
            'url2': raw_data['urls']['url2'].strip()
        }
        user_input = raw_data.get('user_input')

        # Debug log the extracted URLs
        logger.info(f"Extracted URLs: {urls}")

        if not urls or not user_input:
            await comparison_manager.send_status(
                websocket,
                "error",
                "Missing required fields in request"
            )
            return

        # Start the comparison process
        await comparison_manager.start_structured_comparison(websocket, urls, user_input)
    except WebSocketDisconnect:
        logger.info("Client disconnected")
        await comparison_manager.handle_client_disconnect(websocket)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        await comparison_manager.send_status(
            websocket,
            "error",
            "Invalid JSON format"
        )
    except Exception as e:
        logger.error(f"Error in websocket endpoint: {e}")
        await comparison_manager.send_status(
            websocket,
            "error",
            str(e)
        )


async def fetch_and_clean(url: str):
    """Helper function to /compare route to fetch and clean HTML content with exception handling."""
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
    
@router.post("/structured_compare")
async def structured_compare_urls(urls: URLRequest, user_input: UserInput):
    try:
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
            openai_response = call_openai_api_structured(prompt)
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
async def test_openai():
    """ Creates a simple prompt to OpenAI to verify we can use API successfully. """
    try:        
        # do we have an OpenAI API key?
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=400, detail="OpenAI API Key not found")
        else:
            return {"message": call_openai_api("What is the capital of Alaska?")}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
