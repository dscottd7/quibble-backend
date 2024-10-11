import os
from openai import OpenAI

'''
Accepts no parameters, initializes OpenAI with the key stored in the environment variable OPENAI_API_K
'''
def initialize_openai_with_key(api_key):
    # eventually, should replace this with use of environment variable, 
    #  per OpenAI best practices, so we're not sharing a key 
    #  something like api_key=os.environ.get("OPENAI_API_KEY")
    #  - unless we're OK with sharing our key with end users of our app? 
    client = OpenAI(api_key = api_key)    
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
    
    proj_api_key = "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"
    client = initialize_openai_with_key(proj_api_key)
                               
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