import os
from openai import OpenAI
from dotenv import load_dotenv
from tests.get_sample_urls_and_html import get_ebay_url_and_scraped_html, get_amazon_url_and_scraped_html

'''
Calls other functions listed here to initialize OpenAI, create a completion, and return the completion response.
'''
def return_completion_from_prompt(prompt: str):
    client = initialize_openai_with_key()
    completion = create_completion(client, prompt)
    return parse_completion_response(completion)


'''
Initializes OpenAI key stored in the environment variable.
'''
def initialize_openai_with_key():
    load_dotenv() # to use environment variable (OpenAI key)
    client = OpenAI()  # should not need to pass by assigning os.environ.get("OPENAI_API_KEY") to api_key, but that is what's happening here
    return client


'''
Simple "single call" approach from OpenAI "quick start" guide: https://platform.openai.com/docs/quickstart?language-preference=python

This might actually be enough for us - the only "downside" of completions is that they don't maintain state between calls (https://cookbook.openai.com/examples/assistants_api_overview_python, but that might be OK for our use case
'''
def create_completion(client, prompt):
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

'''
Returns only the part of the completion response that we care about
'''
def parse_completion_response(completion):
    output = list()
    for piece in completion.choices:
        output.append(piece.message.content)
    return output[0]



# left in for manual testing, but app should only be calling return_completion_from_prompt()
def main():
    
    # instead of passing hard-coded key, use environment variable
    client = initialize_openai_with_key()
                               
    # get some sample user inputs
    # ebay product description
    url1,url1_html = get_ebay_url_and_scraped_html()
    # amazon product description
    url2,url2_html = get_amazon_url_and_scraped_html()

    prompt = f"Compare the following two products: \n\nProduct 1: \n{url1_html}\n\nProduct 2:\n{url2_html}"
    print(prompt)
    
    # create completion and display output to user
    completion = create_completion(client, prompt)
    output = parse_completion_response(completion)
    print(output)


if __name__ == "__main__":
    main()