#FROM python:3.8.10-slim
# Use Playwright's pre-configured Docker image
#FROM mcr.microsoft.com/playwright/python:v1.35.0-focal

# Use prebuilt image with Python, Chrome, and ChromeDriver - https://github.com/joyzoursky/docker-python-chromedriver/blob/master/py-debian/3.11-selenium/Dockerfile
#FROM joyzoursky/python-chromedriver:latest

# alternative to the above - use python image and install chrome and chromedriver
FROM python:3.11

# Install prerequisites
RUN apt-get update && apt-get install -y wget gnupg unzip

# Add Google Chrome's GPG key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg

# Add Google Chrome's repository (using amd64 here)
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set display port to avoid crash
ENV DISPLAY=:99
# - end of stuff from joyzoursky

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

# TO BUILD IMAGE IN DOCKER HUB REPO: docker build -t jbh14/quibble-backend:1.0.13 .
# TO PUSH IMAGE TO DOCKER HUB (login to docker first): docker push jbh14/quibble-backend:1.0.4

# TO COMPOSE UP (uses compose.yml file): docker-compose up --build
# - creates image and runs container.  "--build" flag is to rebuild the image if it already exists
