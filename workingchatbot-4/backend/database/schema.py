from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./data/db.sqlite3"

# ✅ Delete old DB if schema changed (only for dev/testing)
if not os.path.exists("data/db.sqlite3"):
    os.makedirs("data", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    filename = Column(String, unique=True, index=True)
    filepath = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, index=True)
    question_text = Column(String)
    answer_text = Column(String)
    #created_at = Column(DateTime, default=datetime.utcnow)
