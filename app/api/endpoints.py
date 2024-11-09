import asyncio
from fastapi import APIRouter, HTTPException, Query
from app.models.url_request import URLRequest
from app.models.user_input import UserInput
from app.models.selected_categories import SelectedCategories
from app.services.prompt_service import create_prompt, create_summary_prompt, create_comparison_prompt
from app.services.openai_service import call_openai_api
from app.models.scrape_request import ScrapeRequest
from app.services.get_with_selenium import get_with_selenium
from app.services.clean_html import clean_html
from sse_starlette.sse import EventSourceResponse
from typing import List
import json

import os

# Initialize the router
router = APIRouter()


""" API route to handle POST request for product comparson """
@router.post("/compare")
async def compare_urls(urls: URLRequest, user_input: UserInput):
    try:
        # Validate selected categories
        SelectedCategories.validate_categories(user_input.selected_categories)

        # Scrape HTML and return only the page content for both URLs
        try:
            url1_html = await asyncio.get_event_loop().run_in_executor(None, get_with_selenium, str(urls.url1))
            parsed_url1_html = clean_html(url1_html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        try:
            url2_html = await asyncio.get_event_loop().run_in_executor(None, get_with_selenium, str(urls.url2))
            parsed_url2_html = clean_html(url2_html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # use OpenAI to compare the two products
        # - @TODO prompt formation should be done in a separate function as we get more complex
        # - @Create a prompt for OpenAI API using prompt_service
        prompt = create_prompt(parsed_url1_html, parsed_url2_html, user_input.selected_categories, user_input.user_preference)

        # Call OpenAI API for comparison
        openai_response = call_openai_api(prompt)
        return {"comparison": openai_response}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sse-compare", response_class=EventSourceResponse)
async def sse_compare_urls(
    url1: str = Query(..., description="First URL"),
    url2: str = Query(..., description="Second URL"),
    selected_categories: List[str] = Query(..., description="Selected categories", delimiter=","),
    user_preference: str = Query(..., description="User preference")
):
    """API route to handle product comparison using SSE"""
    async def event_generator():
        try:

            # Get summaries for each product
            try:
                url1_html = await asyncio.get_event_loop().run_in_executor(
                    None, get_with_selenium, str(url1)
                )
                url2_html = await asyncio.get_event_loop().run_in_executor(
                    None, get_with_selenium, str(url2)
                )
                parsed_url1_html = clean_html(url1_html)
                summary_prompt1 = create_summary_prompt(
                    parsed_url1_html, selected_categories, user_preference
                )
                summary1 = call_openai_api(summary_prompt1)
                yield {
                    "event": "summary1",
                    "data": json.dumps({"summary": summary1})
                }
                parsed_url2_html = clean_html(url2_html)
                summary_prompt2 = create_summary_prompt(
                    parsed_url2_html, selected_categories, user_preference
                )
                summary2 = call_openai_api(summary_prompt2)
                yield {
                    "event": "summary2",
                    "data": json.dumps({"summary": summary2})
                }
            except Exception as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": f"Error processing URL: {str(e)}"})
                }
                return  # Exit if a URL fails

            # Generate comparison
            try:
                comparison_prompt = create_comparison_prompt(
                    summary1, summary2
                )
                comparison = call_openai_api(comparison_prompt)
                yield {
                    "event": "comparison",
                    "data": json.dumps({"comparison": comparison})
                }
            except Exception as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": f"Error generating comparison: {str(e)}"})
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())


""" Experimental route to handle scraping for user agent blocking and JS rendering """
@router.post("/scrape")
def scrape_url(request: ScrapeRequest):
    try:
        # Using playwright to render page and express any JavaScript
        content = get_with_selenium(str(request.url))
        return {"text": clean_html(content)}  # removed request.selector

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


""" Created a route to test OpenAi itegration independently. 
    This should be modified. Current function is not working """
@router.post("/openai-test")
async def test_openai():
    try:

        # do we have an OpenAI API key?
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=400, detail="OpenAI API Key not found")
        else:
            return {"message" : call_openai_api("What is the capital of Alaska?")} 

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
