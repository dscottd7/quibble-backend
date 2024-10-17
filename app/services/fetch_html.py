import requests
from fastapi import HTTPException


# Fetch HTML from URL
def fetch_html(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()

        return response.text

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {url}, {str(e)}")
