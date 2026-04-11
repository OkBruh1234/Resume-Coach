import os
import requests
import google.auth
from google.auth.transport.requests import Request

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"c:\Users\KIIT\Downloads\Toy-Project\backend\gcp_key.json"

print("Checking Vertex AI Model Availability...")
try:
    credentials, project = google.auth.default()
    credentials.refresh(Request())
    
    url = "https://us-central1-aiplatform.googleapis.com/v1/projects/bootcamp-project-490706/locations/us-central1/publishers/google/models"
    headers = {"Authorization": f"Bearer {credentials.token}"}
    
    res = requests.get(url, headers=headers)
    print(f"Status: {res.status_code}")
    data = res.json()
    
    if "models" in data:
        print(f"Found {len(data['models'])} models available to your project.")
        gemini_models = [m['name'] for m in data['models'] if 'gemini' in m['name'].lower()]
        if gemini_models:
            print("Gemini Models Available:")
            for m in gemini_models:
                print(" -", m)
        else:
            print("NO Gemini models available! Only:", [m['name'] for m in data['models'][:5]])
    else:
        print("Response:", data)
except Exception as e:
    print("Error:", e)
