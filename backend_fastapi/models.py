from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String, nullable=True) # Native Password System
    is_pro = Column(Integer, default=0) # 0 = Free, 1 = Pro (SQLite optimization)
    
    analyses = relationship("ResumeAnalysis", back_populates="user")

class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resume_file = Column(String, index=True)
    job_description = Column(Text)
    ats_score = Column(String)
    gap_analysis = Column(JSON)
    chat_history = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="analyses")
