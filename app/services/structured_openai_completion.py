from openai import OpenAI
from dotenv import load_dotenv
from fastapi import HTTPException
import os
import logging
from app.models.product_comparison import ProductComparison

logger = logging.getLogger(__name__)


def structured_completion_from_prompt(prompt: str):
    client = initialize_openai_with_key()
    if not client:
        return "Error: OpenAI client initialization failed."
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            response_format=ProductComparison
        )
        comparison = completion.choices[0].message.parsed
        return comparison
    except Exception as e:
        logger.error(f"Failed to create completion: {str(e)}")
        raise


def initialize_openai_with_key():
    '''Initializes OpenAI key stored in the environment variable.'''
    load_dotenv()  # to use environment variable (OpenAI key)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found in environment variables.")
        raise HTTPException(status_code=500, detail="OpenAI API key is missing. Please set the API key in environment variables.")
    client = OpenAI(api_key=api_key)  # Initialize with the API key
    return client
