import logging
from app.models.selected_categories import SelectedCategories
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)


def create_prompt(url1_html: str, url2_html: str, selected_categories: list, user_preference: str)-> str:

    # Validate HTML content
    if not url1_html.strip():
        logger.error("Empty content received for Product 1 HTML.")
        raise HTTPException(status_code=400, detail="Product 1 content is missing or empty.")

    if not url2_html.strip():
        logger.error("Empty content received for Product 2 HTML.")
        raise HTTPException(status_code=400, detail="Product 2 content is missing or empty.")

    # If no categories are provided, use default categories
    if not selected_categories:
        logger.info("No categories provided, using default categories.")
        selected_categories = SelectedCategories.get_default_categories()

    # Check if user preference is empty, provide a default message
    if not user_preference:
        logger.info("No custom preferences provided, using default message.")
        user_preference = "No additional preferences provided"

     # Build a comparison prompt based on user input and selected categories
    categories_text = ', '.join(selected_categories)
    prompt = (
        f"Compare the following products based on the categories: {categories_text}.\n\n"
        f"Product 1: {url1_html}\n\nProduct 2: {url2_html}.\n\n"
        f"User preference: {user_preference}.\n"
        f"Provide a recommendation based on the selected categories.\n"
        f"Provide a title for this set of comparison."   # Add a title for the comparison
    )
    return prompt
