# quibble-backend
Backend application for Quibble

## Project Overview
This project is a web-based application designed to compare products from different websites. It accepts two URLs, attempts to scrape product information from those web pages (using Selenium), and then prompts OpenAI to generate a detailed comparison between the products based on factors provided by the application's frontend.

## Installation
1. Clone the repository: 
```
git clone <repository_url>
```
2. If needed, install Python 3.11 (`undetected_chromedriver`, used in this app, is currently not supported by Python 3.12+)
```
brew install python@3.11                    # Mac
winget install -e --id Python.Python.3.11   # Windows
```
3. Create and activate a virtual environment: 
```
python3.11 -m venv .venv   # Mac
py -3.11 -m venv .venv     # Windows

source .venv/bin/activate  # Mac/Linux
.\venv\Scripts\activate    # Windows
```
4. Install required dependencies:
```
pip install -r requirements.txt
```
5. Set up environment variables:
- Create a `.env` file in the root of your project with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
FRONTEND_URL=http://localhost:3000
```
- **NOTE**: if deploying to cloud, replace `FRONTEND_URL` with the URL of the deployed frontend you plan to connect with, so CORS settings do not block traffic from your deployed frontend app.
6. Run the application:
```
uvicorn app.main:app --reload
```
7. Access Swagger for testing:
- Navigate to `http://127.0.0.1:8000/docs` in your browser to access the Swagger UI and test API routes (websockets will not appear there).
