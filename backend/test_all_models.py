import os
from langchain_google_vertexai import ChatVertexAI

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"c:\Users\KIIT\Downloads\Toy-Project\backend\gcp_key.json"

models_to_test = [
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-flash",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-002",
    "gemini-1.0-pro-001",
    "gemini-1.0-pro-002",
    "gemini-pro"
]

print("Scanning for accessible Gemini models on your Google Cloud Project...", flush=True)

success_model = None
for model in models_to_test:
    try:
        print(f"Testing {model}... ", end="", flush=True)
        llm = ChatVertexAI(project="bootcamp-project-490706", location="us-central1", model_name=model)
        res = llm.invoke("Hi")
        print("SUCCESS!!!")
        success_model = model
        break
    except Exception as e:
        print(f"FAILED (404/403)")

if success_model:
    print(f"\nFOUND_WORKING_MODEL={success_model}")
else:
    print("\nALL MODELS FAILED. This usually indicates Google Cloud billing is disabled or Vertex API lacks region quotas.")
