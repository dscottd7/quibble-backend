from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import endpoints  # Import routes from endpoints.py
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OpenAI API Key not found in environment variables.")
    raise HTTPException(status_code=500, detail="Critical environment variable OPENAI_API_KEY is missing.")
# Log the API key only for testing in development mode
logger.info(f"OpenAI API Key loaded: {'***' if OPENAI_API_KEY else 'Missing'}")  # Mask key in logs

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,  # Enable sending cookies and authentication from frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes from endpoints.py
app.include_router(endpoints.router)


@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"message": "Product Comparison API running"}
