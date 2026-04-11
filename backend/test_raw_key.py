import urllib.request
import json

api_key = "AIzaSyBcyKeuYO9QBgN0fWmZgiptlGFDUgte8XY"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

headers = {'Content-Type': 'application/json'}
data = json.dumps({"contents": [{"parts":[{"text": "Hi"}]}]}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers=headers, method='POST')
try:
    print("Testing RAW REST API with AI Studio Key...")
    with urllib.request.urlopen(req) as response:
        print("STATUS: 200 SUCCESS!")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"ERROR: {e}")
