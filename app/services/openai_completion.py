from openai import OpenAI
from dotenv import load_dotenv
from fastapi import HTTPException
import os
import logging
import openai

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def return_completion_from_prompt(prompt: str):
    '''Calls other functions listed here to initialize OpenAI, create a completion, and return the completion response.'''
    client = initialize_openai_with_key()
    if not client:
        return "Error: OpenAI client initialization failed."

    try:
        completion = create_completion(client, prompt)
        return parse_completion_response(completion)
    except openai.error.AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}. Please check the OpenAI API key.")
        raise HTTPException(status_code=500, detail="Authentication error with OpenAI API.")
    except openai.error.InvalidRequestError as e:
        logger.error(f"Invalid request: {str(e)}. Check the prompt or model specifications.")
        raise HTTPException(status_code=400, detail="Invalid request to OpenAI API.")
    except openai.error.RateLimitError as e:
        logger.error(f"Rate limit exceeded: {str(e)}. Please try again later.")
        raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}.")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while calling OpenAI API.")


def initialize_openai_with_key():
    '''Initializes OpenAI key stored in the environment variable.'''
    load_dotenv()  # to use environment variable (OpenAI key)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found in environment variables.")
        raise HTTPException(status_code=500, detail="OpenAI API key is missing. Please set the API key in environment variables.")
    client = OpenAI(api_key=api_key)  # Initialize with the API key
    return client


def create_completion(client, prompt):
    '''Simple "single call" approach to OpenAI API'''
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion
    except Exception as e:
        logger.error(f"Failed to create completion: {str(e)}")
        raise


def parse_completion_response(completion):
    '''Returns only the part of the completion response that we care about'''
    try:
        output = [piece.message.content for piece in completion.choices]
        return output[0] if output else "No response content found."
    except Exception as e:
        logger.error(f"Failed to parse completion response: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse OpenAI completion response.")
