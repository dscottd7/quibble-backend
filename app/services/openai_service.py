# import openai
# import time
# import os
# import logging
# from fastapi import HTTPException
# from dotenv import load_dotenv
# from app.services.openai_completion import return_completion_from_prompt
# from app.services.openai_thread import return_thread_from_prompt

# # Load environment variables
# load_dotenv()

# # Get logger for the current module
# logger = logging.getLogger(__name__)


# def call_openai_api(prompt: str):
#     '''Function to call OpenAI API with the given prompt and return the response.'''
#     logger.info(f"Received prompt for OpenAI API call")  # removed printing of {prompt} to make output more readable

#     # check that we have an OpenAI key
#     api_key = os.getenv("OPENAI_API_KEY")
#     if not api_key:
#         logger.error("OpenAI API key not found.")
#         raise HTTPException(status_code=500, detail="OpenAI API key not configured. Please check environment variables.")

#     openai_prompt_type = "completion"  # toggle to "thread" if desired
#     start_time = time.perf_counter()  # start stopwatch

#     try:
#         # Call OpenAI API
#         if openai_prompt_type == "completion":
#             response = return_completion_from_prompt(prompt)
#         else:
#             response = return_thread_from_prompt(prompt)

#         process_time = time.perf_counter() - start_time  # stopwatch OFF
#         logger.info(f"Received response from OpenAI API: {response}")
#         logger.info(f"Processed OpenAI {openai_prompt_type} in {process_time:.4f} seconds.")

#         return response

#     except openai.error.AuthenticationError:
#         logger.error("Authentication error with OpenAI API.")
#         raise HTTPException(status_code=403, detail="Authentication failed. Check the OpenAI API key.")

#     except openai.error.RateLimitError:
#         logger.warning("Rate limit exceeded for OpenAI API.")
#         raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded. Please try again later.")

#     except openai.error.OpenAIError as e:
#         logger.error(f"OpenAI API error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

#     except Exception as e:
#         logger.error(f"Unexpected error calling OpenAI API: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
