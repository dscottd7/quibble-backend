from fastapi import APIRouter, HTTPException
from app.models.url_request import URLRequest
from app.models.scrape_request import ScrapeRequest
from app.services.fetch_html import fetch_html
from app.services.parse_html import parse_html
from app.services.openai_service import call_openai_api
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer, reactor
from twisted.internet.defer import ensureDeferred
from app.services.spider import ExampleSpider
import asyncio

runner = CrawlerRunner()
router = APIRouter()


def install_reactor():
    try:
        from twisted.internet import asyncioreactor
        asyncioreactor.install()
    except Exception as e:
        if "reactor already installed" not in str(e):
            raise

@defer.inlineCallbacks
def run_scrapy_crawl(url):
    spider = ExampleSpider(url=url)
    yield runner.crawl(spider)
    
    # Debugging the scraped data
    print("Scraped Data:", spider.scraped_data)  # Add this to inspect the data
    
    # Ensure the returned data is JSON serializable
    if not isinstance(spider.scraped_data, (list, dict)):
        raise ValueError("Scraped data must be a list or dictionary")
    
    return spider.scraped_data

@router.post("/scrapy")
async def scrapy(request: ScrapeRequest):
    url = request.url

    try:
        # Ensure the reactor is installed
        install_reactor()

        # Run the Scrapy crawl in a separate thread
        loop = asyncio.get_event_loop()
        scraped_data = await loop.run_in_executor(None, lambda: ensureDeferred(run_scrapy_crawl(url)))

        # Return a response with the scraped data
        return {"status": "scraping complete", "url": url, "data": scraped_data}
    except Exception as e:
        # Handle exceptions and return appropriate error
        raise HTTPException(status_code=500, detail=str(e))


""" API route to handle POST request for product comparson
    Other two routes can be integrated back to this route after successful independent testing """
@router.post("/compare")
async def compare_urls(urls: URLRequest):
    try:
        # Fetch HTML content from the provided URLs
        url1_html = await fetch_html(urls.url1)
        url2_html = await fetch_html(urls.url2)

        # Parse HTML and return only the page content for both URLs
        parsed_url1_html = await parse_html(url1_html)
        parsed_url2_html = await parse_html(url2_html)

        # use OpenAI to compare the two products
        # - @TODO prompt formation should be done in a separate function as we get more complex
        prompt = f"Compare the following two products: \n\nProduct 1: \n{parsed_url1_html}\n\nProduct 2:\n{parsed_url2_html}"
        openai_response = await call_openai_api(prompt)
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
        url1_html = await fetch_html(urls.url1)
        url2_html = await fetch_html(urls.url2)

        # Parse HTML and return only the page content for both URLs
        parsed_url1_html = await parse_html(url1_html)
        parsed_url2_html = await parse_html(url2_html)

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
        prompt = f"Compare the following two products: \n\nProduct 1: \n{urls.url1}\n\nProduct 2:\n{urls.url2}"

        # Call OpenAI API to get comparison results
        openai_response = await call_openai_api(prompt)

        # Return comparison response
        return {"comparison": openai_response.get("choices")[0].get("text")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))