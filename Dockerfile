# use python image
FROM --platform=$BUILDPLATFORM python:3.11

# Install prerequisites
RUN apt-get update && apt-get install -y wget gnupg unzip

# Define environment variables for architecture detection
ARG TARGETPLATFORM
RUN echo "Building for platform: $TARGETPLATFORM"

<<<<<<< Updated upstream
# Add Google Chrome's repository (using amd64 here)
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
=======
# Conditional install based on architecture
RUN if [ "$(echo $TARGETPLATFORM | grep 'arm64')" ]; then \
        # Install dependencies for Chromium on ARM
        apt-get install -y libnss3 libxss1 libasound2 fonts-liberation; \
        # Download Chromium for ARM64
        wget https://github.com/chromium/chromium/releases/download/109.0.5414.74/chromium-109.0.5414.74-linux-arm64.deb -O /tmp/chromium.deb; \
        dpkg -i /tmp/chromium.deb || apt-get -f install -y; \
        rm /tmp/chromium.deb; \
        # Download and install ChromeDriver for ARM64
        wget https://chromedriver.storage.googleapis.com/109.0.5414.74/chromedriver_linux64.zip -O /tmp/chromedriver.zip; \
        unzip /tmp/chromedriver.zip -d /usr/local/bin/; \
        rm /tmp/chromedriver.zip; \
    else \
        # Add Google Chrome's GPG key and install Chrome for amd64
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
        apt-get update && apt-get install -y google-chrome-stable && \
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip" && \
        unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
        rm /tmp/chromedriver.zip; \
    fi
>>>>>>> Stashed changes

# Set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /dockerapp 

COPY . /dockerapp

RUN pip install -r requirements.txt

<<<<<<< Updated upstream
EXPOSE 8000

# Set the command using JSON format for improved stability
CMD ["uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]
=======
# Expose port 8000
EXPOSE 8000

# Launch uvicorn server
CMD ["uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]
>>>>>>> Stashed changes
