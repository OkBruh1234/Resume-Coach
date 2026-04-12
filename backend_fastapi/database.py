from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

# Google Cloud Storage Native Mount check
db_dir = "/mnt/data"
if os.path.exists(db_dir):
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_dir}/resume.db"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/resume.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
