from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from app.api import endpoints  # Import routes from endpoints.py
import os

# Load environment variables
load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY')}")# For testing purpose

# Initialize FastAPI app
app = FastAPI()

# URLs we'll accept traffic from
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")  # For local testing - defaults to localhost
cloud_run_frontend_url = "https://quibble-358506364187.us-central1.run.app" # our deployed frontend app URL

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, cloud_run_frontend_url],
    allow_credentials=True, # Enable sending cookies and authentication from frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes from endpoints.py
app.include_router(endpoints.router)

# Root route for testing purposes
@app.get("/")
async def root():
    return {"message": "Product Comparison API running"}