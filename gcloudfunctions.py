import os
from google.cloud import secretmanager

def access_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    secret_version_name = f"projects/64265842032/secrets/TEST_API_KEY/versions/latest"
    response = client.access_secret_version(request={"name": secret_version_name})
    return response.payload.data.decode('UTF-8')

def placeholder_function(request):
    secret_value = access_secret('your-secret-name')
    return f"Function deployed successfully! Secret: {secret_value}", 200



#gcloud functions deploy placeholder_function --runtime python39 --trigger-http --allow-unauthenticated --source app --entry-point placeholder_function
# STOPPING POINT - gcloud wants to see both main.py and requirements.txt in the root directory