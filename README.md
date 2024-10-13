# quibble-backend
Backend application for Quibble

To run either of the test programs I've built so far, simply run the python program, for example:
    $ python3 CreateCompletionFromPrompt.py

You'll then be prompted to give an input (ask a question, give a prompt, whatever!) and the assistants I've set up in the program will respond.  
Since the "CreateThreadAndRun.py" program creates an asynchronous thread, it will take a little longer than the other program, but I suspect that we may end up needing to use threads given the size of the prompts we'll be creating later on.

There are 2 ways to pass the API key for the project in - as a hard-coded variable, or as an environmental variable.  Using a hard-coded variable is less secure and not recommended, plus OpenAI is smart enough to invalidate tokens that are pushed to a GitHub branch.

To use the environmental variable approach to authentication, there are a few steps needed to pass the API key via an environmental variable:
1. Navigate to the project directory
2. Create a virtual environment (Mac instructions here):
    $ python3 -m venv venv
    $ . venv/bin/activate
3. Install requirements (just OpenAI right now):
    $ pip install -r requirements.txt
4. Create a Project API key (https://platform.openai.com/api-keys) if you don't have a valid one already.
5. Add API key to your environment:
    $ OPENAI_API_KEY=yourkeyvalue (replace that with your actual key)
6. Optionally, you can create a ".env" file in your local project directory and save your key there.  The ".gitignore" file will ignore your ".env" file so that your key is not committed to the repo.
7. You should be able to run either of the test programs now, using your project key.