import requests
from io import BytesIO

# Minimal empty PDF
minimal_pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"

url = "http://127.0.0.1:8000/api/analyze/"
files = {"file": ("test.pdf", BytesIO(minimal_pdf), "application/pdf")}
data = {"job_description": "We need a python engineer"}

print("Sending request...")
try:
    response = requests.post(url, files=files, data=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
