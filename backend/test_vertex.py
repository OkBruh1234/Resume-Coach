import os
import time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"c:\Users\KIIT\Downloads\Toy-Project\backend\gcp_key.json"

print("Starting Vertex AI Test...")
try:
    from langchain_google_vertexai import VertexAIEmbeddings
    
    print("Initializing embeddings connection...")
    t0 = time.time()
    embeddings = VertexAIEmbeddings(project="bootcamp-project-490706", location="us-central1", model_name="text-embedding-004")
    
    print("Calling Google Cloud Embed API...")
    res = embeddings.embed_query("Hello world")
    
    print(f"Success! Extracted {len(res)} dimensions in {time.time()-t0:.2f}s")
except Exception as e:
    print(f"\n--- ERROR ---")
    print(str(e))
