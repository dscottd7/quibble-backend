from app.models.selected_categories import SelectedCategories

def create_prompt(url1_html: str, url2_html: str, selected_categories: list, user_preference: str)-> str:

    # Check empty user input
    # If no categories are provided, use default categories
    if not selected_categories:
        selected_categories = SelectedCategories.get_default_categories()
    # Check if user preference is empty, provide a default message
    if not user_preference:
        user_preference = "No specific preference provided"

     # Build a comparison prompt based on user input and selected categories
    categories_text = ', '.join(selected_categories)
    prompt = (
        f"Compare the following products based on the categories: {categories_text}.\n\n"
        f"Product 1: {url1_html}\n\nProduct 2: {url2_html}.\n\n"
        f"User preference: {user_preference}.\n"
        f"Provide a recommendation based on the selected categories."
    )
    return prompt