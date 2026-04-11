import os
import shutil
import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, Depends, HTTPException, UploadFile, Form, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any

# Load environment variables cleanly
from dotenv import load_dotenv
load_dotenv()

import models, database, utils

models.Base.metadata.create_all(bind=database.engine)

# Dynamically patch SQLite constraints gracefully for rolling updates
from sqlalchemy import text
try:
    with database.engine.connect() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN is_pro INTEGER DEFAULT 0"))
        connection.commit()
except Exception as e:
    pass # Expected. The column exists.

app = FastAPI(title="Resume Coach AI Engine")

# CORS Middleware (Perfectly mirrors Django-CORS-Headers)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import hashlib

class RegisterPayload(BaseModel):
    email: str
    name: str
    password: str

@app.post("/api/register/")
def register(payload: RegisterPayload, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="EMAIL_EXISTS")
    if not payload.password:
        raise HTTPException(status_code=400, detail="Missing matching password input")
    hashed = hashlib.sha256(payload.password.encode()).hexdigest()
    user = models.User(email=payload.email, name=payload.name, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": str(user.id), "user": {"id": user.id, "name": user.name, "email": user.email, "is_pro": bool(user.is_pro)}}

class LoginPayload(BaseModel):
    email: str
    password: str = None
    is_oauth: bool = False
    name: str = None

@app.post("/api/google-login/")
def google_login(payload: dict, db: Session = Depends(database.get_db)):
    from google.oauth2 import id_token
    import google.auth.transport.requests
    
    token = payload.get("credential")
    if not token:
        raise HTTPException(status_code=400, detail="Missing Token")
         
    try:
        request = google.auth.transport.requests.Request()
        idinfo = id_token.verify_oauth2_token(token, request, "541990120066-u0ifhuki32pdpddv5dsklh3tqvq96qta.apps.googleusercontent.com")
        
        email = idinfo["email"]
        name = idinfo.get("name", "Google User")
        
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(email=email, name=name, password_hash=None)
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return {"token": str(user.id), "user": {"id": user.id, "name": user.name, "email": user.email, "is_pro": bool(user.is_pro)}}
         
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google Token: {str(e)}")

@app.post("/api/login/")
def login(payload: LoginPayload, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    
    if payload.is_oauth:
        if not user:
            user = models.User(email=payload.email, name=payload.name or "OAuth User", password_hash=None)
            db.add(user)
            db.commit()
            db.refresh(user)
    else:
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")
        if not payload.password:
            raise HTTPException(status_code=400, detail="Missing password input")
        hashed = hashlib.sha256(payload.password.encode()).hexdigest()
        if user.password_hash != hashed:
            raise HTTPException(status_code=401, detail="INVALID_CREDENTIALS")

    return {"token": str(user.id), "user": {"id": user.id, "name": user.name, "email": user.email, "is_pro": bool(user.is_pro)}}

class UpgradePayload(BaseModel):
    user_id: str

@app.post("/api/upgrade-pro/")
def upgrade_user(payload: UpgradePayload, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == int(payload.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_pro = 1
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Upgraded to Pro."}


@app.get("/api/user/{user_id}/history/")
def get_user_history(user_id: int, db: Session = Depends(database.get_db)):
    history = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.user_id == user_id).order_by(models.ResumeAnalysis.created_at.desc()).all()
    res = []
    for h in history:
        # Heavily truncate job descriptions to keep the sidebar cards tight and premium
        raw_job = h.job_description or "General Analysis"
        job_title = (raw_job[:45] + "...") if len(raw_job) > 45 else raw_job
        date_str = str(h.created_at).split(" ")[0] if h.created_at else "Today"
        res.append({"id": h.id, "ats_score": h.ats_score, "date": date_str, "job": job_title})
    return {"history": res}

@app.get("/api/history/{history_id}")
def get_history_detail(history_id: int, db: Session = Depends(database.get_db)):
    h = db.query(models.ResumeAnalysis).filter(models.ResumeAnalysis.id == history_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Re-extract the physical PDF text dynamically from local disk map since it saves SQL DB memory
    text = ""
    try:
        import pdfplumber
        if os.path.exists(h.resume_file):
            with pdfplumber.open(h.resume_file) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except Exception as e:
        text = f"Warning: Historical PDF is unreadable. {str(e)}"

    score_val = int(h.ats_score) if str(h.ats_score).isdigit() else 0
    match_level = "High" if score_val >= 75 else ("Medium" if score_val >= 50 else "Low")

    return {
        "job_description": h.job_description,
        "ats_score": h.ats_score,
        "ats_match_level": match_level,
        "gap_analysis": h.gap_analysis,
        "resume_text": text
    }

@app.post("/api/analyze/")
def analyze_resume(
    job_description: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Form(None),
    db: Session = Depends(database.get_db)
):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=401, detail="Backend failed to read GEMINI_API_KEY from `.env`. Recreate the file or set the global variable!")

    # Native File Saving handling (Replacing Django's Media Handler)
    os.makedirs("./media/resumes", exist_ok=True)
    file_location = f"./media/resumes/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    import pdfplumber
    try:
        with pdfplumber.open(file_location) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF bytes: {str(e)}")

    try:
        rag_result = utils.analyze_resume_with_rag(text, job_description)
        score = rag_result.get("ats_score", "Unknown")
        match_level = rag_result.get("ats_match_level", "Unknown")
        gaps = rag_result.get("gap_analysis", {})
    except Exception as e:
        score = "50"
        match_level = "Medium"
        gaps = {
            "missing_keywords": ["FastAPI AI Backend Error"],
            "suggestions": f"Critical AI Pipeline Blockade: {str(e)}"
        }

    analysis_id = None
    if user_id and user_id != "null" and user_id != "":
        analysis = models.ResumeAnalysis(
            user_id=int(user_id),
            resume_file=file_location,
            job_description=job_description,
            ats_score=score,
            gap_analysis=gaps
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        analysis_id = analysis.id

    return {
        "message": "Analysis successful.",
        "data": {
            "id": analysis_id,
            "ats_score": score,
            "ats_match_level": match_level,
            "gap_analysis": gaps,
            "resume_text": text
        }
    }

# Pydantic schemas forcefully type-check incoming JSONs to prevent breaks
class ChatPayload(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    context: Dict[str, Any] = {}
    user_id: str = None

@app.post("/api/chat/")
def chat(payload: ChatPayload):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=401, detail="Missing API Key!")
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    try:
        # LangChain integrates identically to how we handled it in Django
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

        sys_prompt = "You are an expert Resume Coach. Help the user improve their resume. CRITICAL RULE: You must keep your answers EXTREMELY short, conversational, and punchy. Never exceed 2 to 3 sentences unless the user explicitly asks for a long, detailed rewrite. Do not hallucinate massive rambling lists."
        if payload.context:
            sys_prompt += f"\n\nContext from their recent resume scan:\nTarget Job: {payload.context.get('job_desc', 'N/A')}\nATS Match Level: {payload.context.get('ats_match_level', 'Unknown')}\nATS Score: {payload.context.get('ats_score', 'N/A')}/100\nMissing Keywords: {payload.context.get('gap_analysis', {}).get('missing_keywords', [])}\nSuggestions: {payload.context.get('gap_analysis', {}).get('suggestions', 'None')}\n\n[USER RESUME CONTENT]:\n{payload.context.get('resume_text', 'No resume text provided.')}"

        messages = [SystemMessage(content=sys_prompt)]
        for msg in payload.history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content")))
            else:
                messages.append(AIMessage(content=msg.get("content")))

        messages.append(HumanMessage(content=payload.message))

        response = llm.invoke(messages)
        return {"response": response.content}
    except Exception as e:
        return {"response": f"AI Studio Connection Issue: {str(e)}"}
