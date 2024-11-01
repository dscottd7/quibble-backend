import os
from openai import OpenAI
import time
from dotenv import load_dotenv
from app.services.tests.get_sample_urls_and_html import get_ebay_url_and_scraped_html, get_amazon_url_and_scraped_html


# more steps involved in setting up threads than completion approach, but gives us more options for customization
# helpful reference for this approach: https://cookbook.openai.com/examples/assistants_api_overview_python

'''
Calls other functions listed here to initialize OpenAI, create a completion, and return the completion response.
'''
def return_thread_from_prompt(prompt: str):
    client = initialize_openai_with_key()
    assistant = create_assistant(client)
    thread = create_thread(client)
    add_message_to_thread(client, thread, "user", prompt)
    run = run_thread(client, assistant, thread)
    finished_run = wait_on_run_to_finish(client,thread,run)
    messages = list_messages_in_thread(client,thread)
    response = get_response_from_messages(messages)
    return response


'''
Initializes OpenAI key stored in the environment variable.
'''
def initialize_openai_with_key():
    load_dotenv() # to use environment variable (OpenAI key)
    client = OpenAI()  # should not need to pass by assigning os.environ.get("OPENAI_API_KEY") to api_key, but that is what's happening here
    return client


'''
Optionally accepts the model to use, and returns the assistant created.
'''
def create_assistant(client,model="gpt-3.5-turbo"):
    assistant = client.beta.assistants.create(
        name="MyTestAssistant",
        instructions="You are a friendly and helpful assistant comparing 2 products based on descriptions provided and listing similarities and differences in price, quality, and other attributes you find.  Add information about the products that you think is relevant.",
        model = "gpt-3.5-turbo",
    )
    return assistant

'''
Creates a thread to use with messages. 
Open question - is there benefit to maintaining a thread between multiple messages?
'''
def create_thread(client):
    thread = client.beta.threads.create()
    return thread

'''
Adds a message to the thread - no need to return anything here.
'''
def add_message_to_thread(client, thread, role, content):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role=role,
        content=content,
    )

'''
Runs the thread.  Unlike completions, threads are asynchronous, so we need to wait for the response.
'''
def run_thread(client, assistant, thread):
    response = client.beta.threads.runs.create(        
        thread_id = thread.id, 
        assistant_id = assistant.id
    )
    return response

'''
Waits on a run to finish (blocking, so won't return until the run is complete). 
'''
def wait_on_run_to_finish(client,thread,run):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

'''
List messages in a thread - useful after a run is complete to see what the assistant added.
'''
def list_messages_in_thread(client,thread):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    return messages

'''
Return response from messages - not tested on response with multiple messages,
but works for a single message.
'''
def get_response_from_messages(messages):
    return messages.data[0].content[0].text.value

# left in for manual testing, but app should only be calling return_completion_from_prompt()
def main():
    
    # instead of passing hard-coded key, use environment variable
    client = initialize_openai_with_key()
                               
    # create assistant - can pass specific model if we want
    assistant = create_assistant(client)
    #print(assistant.id)

    # create a thread
    thread = create_thread(client)

    # get some sample user inputs
    # ebay product description
    url1,url1_html = get_ebay_url_and_scraped_html()
    # amazon product description
    url2,url2_html = get_amazon_url_and_scraped_html()
    
    prompt = f"Compare the following two products: \n\nProduct 1: \n{url1_html}\n\nProduct 2:\n{url2_html}"
    print(prompt)

    # add a message to the thread
    add_message_to_thread(client, thread, "user", prompt)

    # run the thread
    run = run_thread(client, assistant, thread)
          
    # since runs are asynchronous, we need to wait for the response
    finished_run = wait_on_run_to_finish(client,thread,run)

    # finally, print messages in thread to see what the assistant added
    messages = list_messages_in_thread(client,thread)

    # parse the thing we want from the messages
    response = get_response_from_messages(messages)
    print(response)

if __name__ == "__main__":
    main()
    