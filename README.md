# Resume Coach AI 🚀

An enterprise-grade, full-stack AI Resume Analyzer designed to parse, analyze, and coach applicants using Google's Gemini Flash architecture. This platform allows applicants to dynamically upload PDFs, compare them against Job Descriptions, and receive instant, highly-accurate gap analysis and ATS Match scoring.

![Resume Coach AI Cover](https://img.shields.io/badge/Status-Production_Ready-success)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)

## ✨ Core Architecture

* **Frontend**: Natively compiled React SPA using Vite, completely styled from scratch using dynamic Glassmorphism layouts, CSS mesh-gradients, and `lucide-react` for iconography. 
* **Authentication**: Engineered custom Google OAuth integration strictly routed to an internal REST multiplexer, removing bulky pip dependencies for pure JWT parsing.
* **Backend Engine**: Lightning-fast REST API powered by FastAPI & Python 3.11. 
* **AI Orchestration**: Built-in RAG pipeline utilizing `langchain` and Google's `gemini-2.5-flash-lite` to actively dissect, score, and evaluate raw PDF byte data against plain text.

## 📂 Project Structure
```text
Toy-Project/
├── backend_fastapi/        # Core FastAPI Logic & DB Models
│   ├── main.py             # Router and OAuth decoders
│   ├── utils.py            # Langchain AI pipelines
│   └── Dockerfile          # Alpine Python 3.11 Container
├── frontend_react/         # React User Interface
│   ├── src/components/     # Dashboard, Analyzer, and Login modules
│   └── Dockerfile          # Nginx Multi-stage compiler (Node 20)
├── docker-compose.yml      # Master Orchestration
└── .gitignore              # Dependency Sequestering
```

## 🚀 Rapid Local Deployment

The application is heavily containerized using `docker-compose`. Absolutely zero local Python or Node installations are required.

1. **Clone the highly-optimized repository:**
```bash
git clone https://github.com/OkBruh1234/Resume-Coach.git
cd Resume-Coach
```

2. **Supply your Google AI Keys:**
Navigate into `backend_fastapi/` and create an `.env` file:
```env
GEMINI_API_KEY=your_studio_key_here
```

3. **Spin up the Cluster:**
```bash
docker-compose up --build
```
* **Frontend UI**: [http://localhost:3000](http://localhost:3000)
* **API Documentation (Swagger)**: [http://localhost:8080/docs](http://localhost:8080/docs)

## ☁️ Cloud Operations
This ecosystem has been rigorously structured to push directly to **Google Cloud Run** using `gcloud builds`. Both environments scale flawlessly at zero-tier constraints.

---
*Developed intensely as a top-tier interview utility tool.*
