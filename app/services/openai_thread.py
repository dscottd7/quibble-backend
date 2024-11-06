import openai
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get logger for the current module
logger = logging.getLogger(__name__)


def return_thread_from_prompt(prompt: str):
    '''Calls other functions listed here to initialize OpenAI, create a completion, and return the completion response.'''
    try:
        client = initialize_openai_with_key()
        assistant = create_assistant(client)
        thread = create_thread(client)
        add_message_to_thread(client, thread, "user", prompt)
        run = run_thread(client, assistant, thread)
        finished_run = wait_on_run_to_finish(client, thread, run)
        messages = list_messages_in_thread(client, thread)
        response = get_response_from_messages(messages)
        return response
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error in return_thread_from_prompt: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in return_thread_from_prompt: {str(e)}")


def initialize_openai_with_key():
    '''Initializes OpenAI key stored in the environment variable.'''
    try:
        client = openai.OpenAI()
        if not client.api_key:
            raise openai.error.AuthenticationError("OpenAI API key is not configured.")
        return client
    except openai.error.AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}. Please check the OpenAI API key.")
        raise
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {str(e)}")
        raise


def create_assistant(client, model="gpt-3.5-turbo"):
    '''Optionally accepts the model to use, and returns the assistant created.'''
    try:
        assistant = client.beta.assistants.create(
            name="MyTestAssistant",
            instructions="You are a friendly and helpful assistant comparing 2 products...",
            model=model,
        )
        return assistant
    except openai.error.OpenAIError as e:
        logger.error(f"Error creating assistant: {str(e)}")
        raise


def create_thread(client):
    '''Creates a thread to use with messages.'''
    try:
        return client.beta.threads.create()
    except openai.error.OpenAIError as e:
        logger.error(f"Error creating thread: {str(e)}")
        raise


def add_message_to_thread(client, thread, role, content):
    '''Adds a message to the thread - no need to return anything here.'''
    try:
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role=role,
            content=content,
        )
    except openai.error.OpenAIError as e:
        logger.error(f"Error adding message to thread: {str(e)}")
        raise


def run_thread(client, assistant, thread):
    '''Runs the thread.  Unlike completions, threads are asynchronous, so we need to wait for the response.'''
    try:
        return client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
    except openai.error.OpenAIError as e:
        logger.error(f"Error running thread: {str(e)}")
        raise


def wait_on_run_to_finish(client, thread, run, max_wait=60):
    '''Waits on a run to finish (blocking, so won't return until the run is complete).'''
    start_time = time.time()
    try:
        while run.status in ["queued", "in_progress"]:
            # Timeout check
            if time.time() - start_time > max_wait:
                raise TimeoutError("Run took too long to finish.")

            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run
    except TimeoutError as e:
        logger.error(f"Timeout error in wait_on_run_to_finish: {str(e)}")
        raise
    except openai.error.OpenAIError as e:
        logger.error(f"Error retrieving run status: {str(e)}")
        raise


def list_messages_in_thread(client, thread):
    '''List messages in a thread - useful after a run is complete to see what the assistant added.'''
    try:
        return client.beta.threads.messages.list(thread_id=thread.id)
    except openai.error.OpenAIError as e:
        logger.error(f"Error listing messages in thread: {str(e)}")
        raise


def get_response_from_messages(messages):
    '''Return response from messages - not tested on response with multiple messages,
but works for a single message.'''
    try:
        return messages.data[0].content[0].text.value
    except IndexError:
        logger.error("No messages found in thread.")
        raise ValueError("No response messages available from the thread.")
    except Exception as e:
        logger.error(f"Error extracting response from messages: {str(e)}")
        raise
