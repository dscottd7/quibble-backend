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