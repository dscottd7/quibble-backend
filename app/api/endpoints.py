from fastapi import APIRouter, HTTPException
from app.models.url_request import URLRequest
from app.models.user_input import UserInput
from app.models.selected_categories import SelectedCategories
from app.services.prompt_service import create_prompt
from app.services.openai_service import call_openai_api
from app.models.scrape_request import ScrapeRequest
from app.services.get_with_selenium import get_with_selenium
# from app.services.get_with_playwright import get_with_playwright
from app.services.clean_html import clean_html

# Initialize the router
router = APIRouter()


""" API route to handle POST request for product comparson """
@router.post("/compare")
def compare_urls(urls: URLRequest, user_input: UserInput):
    try:
        # Validate selected categories
        SelectedCategories.validate_categories(user_input.selected_categories)

        # Scrape HTML and return only the page content for both URLs
        try:
            url1_html = get_with_selenium(str(urls.url1))
            parsed_url1_html = clean_html(url1_html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        try:
            url2_html = get_with_selenium(str(urls.url2))
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
async def test_openai(urls: URLRequest):
    try:
        # Prompts
        prompt = f"Compare the following two products: \n\nProduct 1: \n{url1_html}\n\nProduct 2:\n{url2_html}"

        # Call OpenAI API to get comparison results
        openai_response = call_openai_api(prompt)

        # Return comparison response
        return {"comparison": openai_response.get("choices")[0].get("text")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))