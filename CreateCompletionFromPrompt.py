import os
from openai import OpenAI

'''
Accepts optional API key parameter, 
initializes OpenAI with either the provided key or key stored in the environment variable.
'''
def initialize_openai_with_key(hard_coded_key = None):
    # best practice is to use environment variable, but can also pass in the key directly
    #  Brendan note - we'll want to make a decision here - using the environment variable is more secure, but
    #  might be difficult to facilitate if we are deploying this to the cloud
    if hard_coded_key is not None:
        client = OpenAI(api_key = hard_coded_key)
    else: 
        client = OpenAI()  # should not need to pass by assigning os.environ.get("OPENAI_API_KEY") to api_key, but that is what's happening here
    return client

# simple "single call" approach from OpenAI "quick start" guide
# https://platform.openai.com/docs/quickstart?language-preference=python
# 
# this might actually be enough for us - the only "downside" of completions
# is that they don't maintain state between calls (https://cookbook.openai.com/examples/assistants_api_overview_python)
#  - but that might be OK for our use case
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


def main():
    
    # not secure / best practice, but for now, we'll hard-code the key for easy testing
    brendan_project_key = "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"
    client = initialize_openai_with_key(brendan_project_key)
                               
    # get user input
    prompt = input("Enter a prompt: ")
    
    # create completion and display output to user
    completion = create_completion(client, prompt)
    output = list()
    for piece in completion.choices:
        output.append(piece.message.content)
    print(output)


if __name__ == "__main__":
    main()