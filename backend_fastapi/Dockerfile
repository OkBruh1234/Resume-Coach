FROM python:3.11-slim

WORKDIR /app

# Copy dependency mappings first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend logic
COPY . .

# Expose Webhook point
EXPOSE 8080

# Execute Uvicorn strictly on the global host protocol
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
