import os
from openai import OpenAI
import time
from dotenv import load_dotenv

'''
Initializes OpenAI key stored in the environment variable.
'''
def initialize_openai_with_key():
    # best practice is to use environment variable, instead of passing key directly
    client = OpenAI()  # should not need to pass by assigning os.environ.get("OPENAI_API_KEY") to api_key, but that is what's happening here
    return client


# this is a longer approach, using the steps I thought were needed from the 
#  OpenAI API guide - see CreateCompletion.py for a shorter approach that seems to work
# 
# helpful reference for this approach: https://cookbook.openai.com/examples/assistants_api_overview_python
'''
Optionally accepts the model to use, and returns the assistant created.
'''
def create_assistant(client,model="gpt-3.5-turbo"):
    assistant = client.beta.assistants.create(
        name="MyTestAssistant",
        instructions="You are a friendly and helpful assistant answering question concisely.",
        model = "gpt-3.5-turbo",
    )
    return assistant

'''
Creates a thread to use with messages. 
@TODO - is there benefit to maintaining a thread between messages?
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
Quick and dirty (needs refinement, esp for multiple messages in the thread),
but should work for a simple case.
'''
def get_response_from_messages(messages):
    return messages.data[0].content[0].text.value

def main():
    
    # instead of passing hard-coded key, use environment variable
    client = initialize_openai_with_key()
                               
    # create assistant - can pass specific model if we want
    assistant = create_assistant(client)
    #print(assistant.id)

    # create a thread
    thread = create_thread(client)

    # get user input
    prompt = input("Enter a prompt: ")

    # add a message to the thread
    add_message_to_thread(client, thread, "user", prompt)

    # run the thread
    run = run_thread(client, assistant, thread)
    #print("Run details: ")
    #print(run)
          
    # since runs are asynchronous, we need to wait for the response
    finished_run = wait_on_run_to_finish(client,thread,run)
    #print(finished_run)

    # finally, print messages in thread to see what the assistant added
    messages = list_messages_in_thread(client,thread)
    #print(messages)

    # parse the thing we want from the messages
    response = get_response_from_messages(messages)
    print(response)

if __name__ == "__main__":
    load_dotenv()  # Load the .env file, which should contain our OpenAI key
    main()
    