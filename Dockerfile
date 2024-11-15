# use python image and install chrome and chromedriver (as opposed to using a pre-built image)
FROM python:3.11

# Install prerequisites
RUN apt-get update && apt-get install -y wget gnupg unzip

# Add Google Chrome's GPG key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg

# Add Google Chrome's repository (using amd64 here, since this is the architecture the Google Cloud Run expects for images deployed there)
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set display port to avoid crash (part of Chrome/Driver setup)
ENV DISPLAY=:99

# Set working directory and copy everything into it
WORKDIR /dockerapp 
COPY . /dockerapp

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 8000 - when deploying to Google Cloud, ensure it is sending request here 
EXPOSE 8000

# Launch uvicorn server (using JSON format for improved stability)
CMD ["uvicorn", "app.main:app", "--port", "8000", "--host", "0.0.0.0"]