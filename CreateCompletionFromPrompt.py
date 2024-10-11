import os
from openai import OpenAI

'''
Accepts no parameters, initializes OpenAI with the key stored in the environment variable
'''
def initialize_openai_with_key():
    # best practice is to use environment variable (and GitHub won't let us share keys)
    client = OpenAI()  # should not need to pass by assigning os.environ.get("OPENAI_API_KEY") to api_key
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
    
    client = initialize_openai_with_key()
                               
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