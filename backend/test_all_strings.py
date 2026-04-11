import urllib.request
import json

api_key = "AIzaSyBcyKeuYO9QBgN0fWmZgiptlGFDUgte8XY"
models = [
    "gemini-1.5-flash-latest", 
    "gemini-1.5-flash-001", 
    "gemini-1.5-flash-002", 
    "gemini-1.5-pro", 
    "gemini-1.0-pro", 
    "gemini-2.0-flash-exp", 
    "gemini-2.5-flash",
    "gemini-1.5-flash-8b"
]

print("Pinging AI Studio directly with exact versions...")
working_model = None

for model in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(
        url, 
        data=json.dumps({"contents":[{"parts":[{"text":"Hi"}]}]}).encode('utf-8'), 
        headers={'Content-Type':'application/json'}, 
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"SUCCESS: {model}")
            working_model = model
            break
    except urllib.error.HTTPError as e:
        print(f"FAILED: {model} ({e.code})")

if working_model:
    print(f"\nWINNER: {working_model}")
else:
    print("\nALL MODELS 404'd. API Key is either severely restricted, newly generated and syncing, or completely invalid.")
