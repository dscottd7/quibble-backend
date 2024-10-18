from fastapi import APIRouter, HTTPException
from app.models.url_request import URLRequest
from app.services.fetch_html import fetch_html
from app.services.parse_html import parse_html
from app.services.openai_service import call_openai_api

# Initialize the router
router = APIRouter()


""" API route to handle POST request for product comparson
    Other two routes can be integrated back to this route after successful independent testing """
@router.post("/compare")
async def compare_urls(urls: URLRequest):
    try:
        # Fetch HTML content from the provided URLs
        url1_html = fetch_html(urls.url1)
        url2_html = fetch_html(urls.url2)

        # Parse HTML and return only the page content for both URLs
        parsed_url1_html = parse_html(url1_html)
        parsed_url2_html = parse_html(url2_html)

        # use OpenAI to compare the two products
        # - @TODO prompt formation should be done in a separate function as we get more complex
        prompt = f"Compare the following two products: \n\nProduct 1: \n{parsed_url1_html}\n\nProduct 2:\n{parsed_url2_html}"
        openai_response = call_openai_api(prompt)
        print(openai_response)
        return openai_response



    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


""" Created a route to test HTML scraper func seperately.
    This should be modified. Current function is not working """
@router.post("/scrape")
async def scrape_html(urls: URLRequest):
    try:
        # Fetch HTML content from the provided URLs
        url1_html = fetch_html(urls.url1)
        url2_html = fetch_html(urls.url2)

        # Parse HTML and return only the page content for both URLs
        parsed_url1_html = parse_html(url1_html)
        parsed_url2_html = parse_html(url2_html)

        # Placeholder response
        return {
            "url1_content": parsed_url1_html,
            "url2_content": parsed_url2_html,
            "comparison": "Comparison logic to be added"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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