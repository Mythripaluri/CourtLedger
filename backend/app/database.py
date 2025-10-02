from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from .config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CaseQuery(Base):
    __tablename__ = "case_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    case_type = Column(String(50))
    case_number = Column(String(100))
    year = Column(String(10))
    court_type = Column(String(50))  # "high_court" or "district_court"
    
    # Parsed details
    parties = Column(Text)
    filing_date = Column(String(20))
    next_hearing_date = Column(String(20))
    case_status = Column(String(100))
    judgment_url = Column(String(500))
    
    # Raw response data
    raw_response = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    success = Column(Boolean, default=False)
    error_message = Column(Text)

class CauseList(Base):
    __tablename__ = "cause_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    court_type = Column(String(50))  # "high_court" or "district_court"
    date = Column(String(20))
    
    # Case details
    case_number = Column(String(100))
    sr_no = Column(Integer)
    parties = Column(Text)
    hearing_type = Column(String(100))
    time = Column(String(20))
    court_room = Column(String(50))
    judge = Column(String(200))
    status = Column(String(50))
    
    # PDF generation
    pdf_path = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DriveCommandLog(Base):
    __tablename__ = "drive_command_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_phone = Column(String(20))
    command = Column(String(50))  # LIST, DELETE, MOVE, SUMMARY, etc.
    parameters = Column(Text)  # JSON string of parameters
    
    # Response
    status = Column(String(20))  # "success", "error", "pending"
    response_message = Column(Text)
    error_details = Column(Text)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    execution_time = Column(Float)  # seconds

class FileSummary(Base):
    __tablename__ = "file_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100))  # Google Drive file ID
    file_name = Column(String(500))
    file_path = Column(String(1000))
    file_type = Column(String(50))
    
    # Summary details
    summary_text = Column(Text)
    ai_model = Column(String(50))  # "gpt-4", "claude-3", etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_size = Column(Integer)  # bytes
    last_modified = Column(DateTime)