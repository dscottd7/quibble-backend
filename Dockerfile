FROM python:3.9-slim

WORKDIR /app
# set working directory - might need to change this, in the examples I see it's usually a non-existant
#  directory that is created by the WORKDIR command
#  could it just stay as the current? 

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN playwright install chromium

COPY . .

# this last one only runs when we create a container from the image
CMD uvicorn app.main:app --port=8000 --host=0.0.0.0 --reload


# TO BUILD IMAGE: docker build -t quibblebackend-image1 .
# TO RUN IMAGE: docker run --rm -it -p 8000:8000 quibblebackend-image1 bash
# WHEN RUNNING IMAGE: uvicorn app.main:app --host=0.0.0.0

# TO COMPOSE UP (uses compose.yml file): docker-compose up --build
# - creates image and runs container.  "--build" flag is to rebuild the image if it already exists
