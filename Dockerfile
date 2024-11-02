FROM python:3.8.10-slim

# Install Playwright and dependencies
#RUN pip install playwright && playwright install-deps

WORKDIR /dockerapp

COPY . /dockerapp

RUN pip install -r requirements.txt

EXPOSE 8000

# Install Playwright browsers (like Chromium)
#RUN playwright install chromium

# Set the command using JSON format for improved stability
CMD ["uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]


# TO BUILD IMAGE LOCALLY: docker build -t quibblebackend-image1 .
# TO RUN IMAGE LOCALLY: docker run --rm -it -p 8000:8000 quibblebackend-image1 bash
# WHEN RUNNING IMAGE: uvicorn app.main:app --host=0.0.0.0

# TO BUILD IMAGE IN DOCKER HUB REPO: docker build -t jbh14/quibble-backend:1.0.4 .
# TO PUSH IMAGE TO DOCKER HUB (login to docker first): docker push jbh14/quibble-backend:1.0.4

# TO COMPOSE UP (uses compose.yml file): docker-compose up --build
# - creates image and runs container.  "--build" flag is to rebuild the image if it already exists
