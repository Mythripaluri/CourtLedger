from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Court Case Schemas
class CaseQueryRequest(BaseModel):
    case_type: str
    case_number: str
    year: str
    court_type: str  # "high_court" or "district_court"

class CaseDetails(BaseModel):
    parties: Optional[str] = None
    filing_date: Optional[str] = None
    next_hearing_date: Optional[str] = None
    case_status: Optional[str] = None
    judgment_url: Optional[str] = None

class CaseQueryResponse(BaseModel):
    id: int
    case_type: str
    case_number: str
    year: str
    court_type: str
    details: CaseDetails
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Cause List Schemas
class CauseListRequest(BaseModel):
    court_type: str  # "high_court" or "district_court"
    date: str  # YYYY-MM-DD format
    case_number: Optional[str] = None

class CauseListEntry(BaseModel):
    sr_no: int
    case_number: str
    parties: str
    hearing_type: str
    time: str
    court_room: str
    judge: str
    status: str
    highlighted: bool = False

class CauseListResponse(BaseModel):
    court_type: str
    date: str
    entries: List[CauseListEntry]
    pdf_url: Optional[str] = None
    total_cases: int

# WhatsApp Drive Assistant Schemas
class WhatsAppMessage(BaseModel):
    from_number: str
    message: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class WhatsAppResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class DriveCommand(BaseModel):
    command: str  # LIST, DELETE, MOVE, SUMMARY, etc.
    parameters: Dict[str, Any]
    user_phone: str

class DriveCommandResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

# Drive File Schemas
class DriveFile(BaseModel):
    id: str
    name: str
    type: str  # "folder" or file extension
    size: Optional[int] = None
    modified_time: Optional[str] = None
    web_view_link: Optional[str] = None

class DriveListResponse(BaseModel):
    files: List[DriveFile]
    folder_path: str
    total_files: int

class FileSummaryRequest(BaseModel):
    file_id: str
    file_path: str
    use_ai_model: str = "gpt-4"

class FileSummaryResponse(BaseModel):
    file_id: str
    file_name: str
    summary: str
    ai_model: str
    created_at: datetime

# Integration Schemas
class GoogleAuthResponse(BaseModel):
    auth_url: str
    state: str

class IntegrationStatus(BaseModel):
    service: str
    connected: bool
    last_sync: Optional[datetime] = None
    error: Optional[str] = None

class CalendarEventRequest(BaseModel):
    case_id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

# Error Response Schema
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None