#FROM python:3.8.10-slim
# Use Playwright's pre-configured Docker image
FROM mcr.microsoft.com/playwright/python:v1.35.0-focal

# Install Chrome/Chromium dependencies > this might not be totally necessary if using pre-configured Playwright image
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxkbcommon0 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatk-bridge2.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver and required Python packages
RUN pip install webdriver-manager
RUN pip install playwright selenium && playwright install chromium

# Add ChromeDriver to PATH
ENV PATH="/root/.wdm/drivers/chromedriver/linux64/114.0.5735.90:${PATH}"

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
