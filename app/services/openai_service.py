import openai
import time
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from app.services.openai_completion import return_completion_from_prompt
from app.services.openai_thread import return_thread_from_prompt


# Fetch OpenAI API key from environment variable
""" openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise HTTPException(status_code=500, detail="OpenAI API key not found") """

# Test if the key is loaded
print(f"Loaded OpenAI API Key: {openai.api_key}")

# Function to call OpenAI API
def call_openai_api(prompt: str):
    print("Received prompt:")
    print(prompt)

    try:
            
        # two ways to call OpenAPI - completion vs thread
        # completion is simpler, thread allows more customization and ultimately might be what we want if we are going to open up options
        #  for the user to provide more inputs about the assistant's response, specify response format, etc
        openaiPromptType = "completion"  # @TODO toggle this to "completion" for testing if you'd like
        start_time = time.perf_counter() # stopwatch ON
        if openaiPromptType == "completion":
            response = return_completion_from_prompt(prompt)
        else:
            response = return_thread_from_prompt(prompt)
        process_time = time.perf_counter() - start_time  # stopwatch OFF
        print("")
        print(f"***Processed OpenAI {openaiPromptType} in {process_time:0.4f} seconds***")
        print("")

        # Print the placeholder response
        print("OpenAI Response:")
        #print(response_placeholder["choices"][0]["text"])
        print(response)

        return response #response_placeholder
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calling OpenAI API: {str(e)}")
    