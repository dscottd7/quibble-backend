# quibble-backend
Backend application for Quibble

## Project Overview
This project is a web-based application designed to compare products from different websites. It accepts two URLs, processes their content, and uses AI to generate a detailed comparison between the products. For now, the OpenAI logic is under construction, and the scraping logic is being developed.

## Installation
1. Clone the repository: 
```
git clone <repository_url>
```
2. Create and activate a virtual environment: 
```
python3 -m venv .venv

source .venv/bin/activate  # Use this if you have Mac/Linux
.\venv\Scripts\activate    # Use this if you have Windows
```
3. Install required dependencies:
```
pip install -r requirements.txt

playwright install chromium  # Use this for new /scrape route
```
4. Set up environment variables:
- Create a .env file in the root of your project with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
FRONTEND_URL=http://localhost:3000
```
5. Run the application:
```
uvicorn app.main:app --reload
```
6. Access Swagger for testing:
- Navigate to http://127.0.0.1:8000/docs in your browser to access the Swagger UI and test the /compare API route.

## Team collobration 
In services folder, scraper.py and openai_service.py can be modified and extended based on your development needs. Please feel free to delete any unnecessary functions. 

## Standard Git Workflow for Team Collaboration
1. Check modified files: 
```
git status
```
2. Add and commit changes: 
```
git add <specific-file>
git add .  # To add all changed files
```
3. Ignore runtime files:
- Add for examle .env, venv/, __pycache__/ to .gitignore.
- Save .gitignore
- Remove __pycache__ from Git's tracking with: 
```
git rm --cached -r app/api/__pycache__/  (check the right path by "git status")
git rm --cached -r app/models/__pycache__/
```
- Commit the .gitignore file changes. 
```
git add .gitignore
```
4. Commit changes:
```
git commit -m "Describe changes"
```
5. Pull and push changes to avoid conflicts:
```
git pull origin <branch>
git push origin <branch-name>
```

## Sprint II Project Updates for Quibble_backend
1. Refine LLM prompt to improve response content
- user_input.py (Models): Defines user inputs like selected_categories and user_preference.
- selected_categories.py (Models): Validates the categories selected by the user and provides default categories if no specific ones are selected.
- prompt_service.py (Services): Constructs the final prompt using selected categories, user preference, and parsed product details.
- endpoints.py (API): Integrates all logic to fetch, parse, and create a refined prompt to send to OpenAI based on user input.
