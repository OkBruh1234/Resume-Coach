import os
import requests

# Load from .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

from langchain_google_genai import ChatGoogleGenerativeAI

print("FORCING REMOVAL OF GOOGLE_APPLICATION_CREDENTIALS")
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

try:
    print(f"API Key: {os.environ.get('GEMINI_API_KEY', 'MISSING')[:5]}...")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    print("Invoking model...")
    res = llm.invoke("Hi")
    print("SUCCESS!", res)
except Exception as e:
    print("ERROR:", e)

    print("\nTrying alternative model strings...")
    for mod in ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-1.5-flash-001"]:
        try:
            print(f"Testing {mod}...")
            llm2 = ChatGoogleGenerativeAI(model=mod)
            res2 = llm2.invoke("Hi")
            print("SUCCESS!", res2)
            break
        except Exception as e2:
            print("ERROR", e2)
