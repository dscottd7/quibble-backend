import openai
import time
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from app.services.openai_completion import return_completion_from_prompt
from app.services.openai_thread import return_thread_from_prompt
from app.services.tests.get_sample_urls_and_html import get_ebay_url_and_scraped_html, get_amazon_url_and_scraped_html


# Function to call OpenAI API
def call_openai_api(prompt: str):
    print("Received prompt:")
    print(prompt)

    # check that we have an OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not found")

    try:
        # two ways to call OpenAPI - completion vs thread
        # - completion is simpler, thread allows more customization and ultimately might be what we want if we are going to open up options
        #   for the user to provide more inputs about the assistant's response, specify response format, etc
        
        openaiPromptType = "completion"  # toggle this to "thread" for testing if desired
        start_time = time.perf_counter() # start stopwatch 
        if openaiPromptType == "completion":
            response = return_completion_from_prompt(prompt)
        else:
            response = return_thread_from_prompt(prompt)
        process_time = time.perf_counter() - start_time  # stopwatch OFF
        
        # print processed time
        print("")
        print(f"***Processed OpenAI {openaiPromptType} in {process_time:0.4f} seconds***")
        print("")

        # print response from OpenaI
        print("OpenAI Response:")
        print(response)

        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calling OpenAI API: {str(e)}")
    
if __name__ == "__main__":

    # get some sample user inputs
    # ebay product description
    url1,url1_html = get_ebay_url_and_scraped_html()
    # amazon product description
    url2,url2_html = get_amazon_url_and_scraped_html()
    
    prompt = f"Compare the following two products: \n\nProduct 1: \n{url1_html}\n\nProduct 2:\n{url2_html}"

    call_openai_api(prompt)