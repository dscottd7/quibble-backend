# quibble-backend
Backend application for Quibble

To run either of the test programs I've built so far, simply run the python program, for example:
    $ python3 CreateCompletionFromPrompt.py

You'll then be prompted to give an input (ask a question, give a prompt, whatever!) and the assistants I've set up in the program will respond.  
Since the "CreateThreadAndRun.py" program creates an asynchronous thread, it will take a little longer than the other program, but I suspect that we may end up needing to use threads given the size of the prompts we'll be creating later on.

There are 2 ways to pass the API key for the project in - as a hard-coded variable, or as an environmental variable.  Using a hard-coded variable is less secure and not recommended, but I did it for the purpose of this initial commit, to make playing with this easier for others.  The environmental variable approach may also be difficult to incorporate once we deploy this to the cloud, so we'll have to make a decision there.

If using the environmental variable approach to authentication, there are a few steps needed to pass the API key via an environmental variable:
1. Navigate to the project directory
2. Create a virtual environment:
    $ python3 -m venv venv
    $ . venv/bin/activate
3. Install requirements (just OpenAI right now):
    $ pip install -r requirements.txt
4. Add API key to your environment:
    $ OPENAI_API_KEY=yourkeyvalue
5. You should be able to run either of the test programs now, using my project key.