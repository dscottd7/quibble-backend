import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException

# Fetch HTML from URL
def fetch_html(url: str) ->str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if product title exists
        product_title = soup.find('h1')
        if product_title:
            product_title = product_title.get_text(strip=True)
        else:
            product_title = "Title not found"

        # Check if product description exists
        product_description = soup.find('div', {'class': 'product-description'})
        if product_description:
            product_description = product_description.get_text(strip=True)
        else:
            product_description = "Description not found"

        return f"Product: {product_title}\nDescription: {product_description}"

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {url}, {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing HTML from URL: {url}, {str(e)}")