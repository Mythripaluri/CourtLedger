from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db, CaseQuery, CauseList
from ..schemas import (
    CaseQueryRequest, CaseQueryResponse, CaseDetails,
    CauseListRequest, CauseListResponse, CauseListEntry,
    ErrorResponse
)
from ..services.court_scraper import CourtScraper
from ..services.pdf_generator import PDFGenerator
from ..services.cause_list_manager import CauseListManager, CauseListFilter
from ..services.notification_service import NotificationService
from ..services.demo_data import demo_service

router = APIRouter()

@router.post("/fetch-case", response_model=CaseQueryResponse)
async def fetch_case_details(
    request: CaseQueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Fetch case details from High Court or District Court
    """
    try:
        # Check if case already exists in database
        existing_case = db.query(CaseQuery).filter(
            CaseQuery.case_number == request.case_number,
            CaseQuery.year == request.year,
            CaseQuery.court_type == request.court_type
        ).first()
        
        if existing_case and existing_case.success:
            # Return cached result
            return CaseQueryResponse(
                id=existing_case.id,
                case_type=existing_case.case_type,
                case_number=existing_case.case_number,
                year=existing_case.year,
                court_type=existing_case.court_type,
                details=CaseDetails(
                    parties=existing_case.parties,
                    filing_date=existing_case.filing_date,
                    next_hearing_date=existing_case.next_hearing_date,
                    case_status=existing_case.case_status,
                    judgment_url=existing_case.judgment_url
                ),
                success=existing_case.success,
                error_message=existing_case.error_message,
                created_at=existing_case.created_at
            )
        
        # Create new database entry
        case_query = CaseQuery(
            case_type=request.case_type,
            case_number=request.case_number,
            year=request.year,
            court_type=request.court_type
        )
        db.add(case_query)
        db.commit()
        db.refresh(case_query)
        
        # Use demo data for demonstration purposes
        # In production, this would use the real scraper
        case_data = demo_service.get_case_details(
            request.case_type, request.case_number, request.year
        )
        
        # Update database with scraped data
        case_query.parties = case_data.get("parties")
        case_query.filing_date = case_data.get("filing_date")
        case_query.next_hearing_date = case_data.get("next_hearing_date")
        case_query.case_status = case_data.get("case_status")
        case_query.judgment_url = case_data.get("judgment_url")
        case_query.raw_response = str(case_data)
        case_query.success = True
        
        db.commit()
        db.refresh(case_query)
        
        return CaseQueryResponse(
            id=case_query.id,
            case_type=case_query.case_type,
            case_number=case_query.case_number,
            year=case_query.year,
            court_type=case_query.court_type,
            details=CaseDetails(
                parties=case_query.parties,
                filing_date=case_query.filing_date,
                next_hearing_date=case_query.next_hearing_date,
                case_status=case_query.case_status,
                judgment_url=case_query.judgment_url
            ),
            success=case_query.success,
            created_at=case_query.created_at
        )
        
    except Exception as e:
        # Update database with error
        if 'case_query' in locals():
            case_query.success = False
            case_query.error_message = str(e)
            db.commit()
        
        raise HTTPException(status_code=500, detail=f"Failed to fetch case details: {str(e)}")

@router.post("/fetch-causelist", response_model=CauseListResponse)
async def fetch_cause_list(
    request: CauseListRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Fetch daily cause list from High Court or District Court
    """
    try:
        # Check if cause list already exists for this date
        existing_entries = db.query(CauseList).filter(
            CauseList.court_type == request.court_type,
            CauseList.date == request.date
        ).all()
        
        if existing_entries:
            # Return cached result
            entries = []
            for entry in existing_entries:
                highlighted = (request.case_number and 
                             request.case_number.lower() in entry.case_number.lower())
                entries.append(CauseListEntry(
                    sr_no=entry.sr_no,
                    case_number=entry.case_number,
                    parties=entry.parties,
                    hearing_type=entry.hearing_type,
                    time=entry.time,
                    court_room=entry.court_room,
                    judge=entry.judge,
                    status=entry.status,
                    highlighted=highlighted
                ))
            
            return CauseListResponse(
                court_type=request.court_type,
                date=request.date,
                entries=entries,
                pdf_url=existing_entries[0].pdf_path if existing_entries[0].pdf_path else None,
                total_cases=len(entries)
            )
        
        # Use demo data for demonstration purposes
        # In production, this would use the real scraper
        cause_list_data = demo_service.get_cause_list(request.court_type, request.date)
        
        # Save to database
        entries = []
        for i, case_data in enumerate(cause_list_data):
            cause_list = CauseList(
                court_type=request.court_type,
                date=request.date,
                case_number=case_data.get("case_number", ""),
                sr_no=i + 1,
                parties=case_data.get("parties", ""),
                hearing_type=case_data.get("hearing_type", ""),
                time=case_data.get("time", ""),
                court_room=case_data.get("court_room", ""),
                judge=case_data.get("judge", ""),
                status=case_data.get("status", "Listed")
            )
            db.add(cause_list)
            
            highlighted = (request.case_number and 
                         request.case_number.lower() in case_data.get("case_number", "").lower())
            entries.append(CauseListEntry(
                sr_no=i + 1,
                case_number=case_data.get("case_number", ""),
                parties=case_data.get("parties", ""),
                hearing_type=case_data.get("hearing_type", ""),
                time=case_data.get("time", ""),
                court_room=case_data.get("court_room", ""),
                judge=case_data.get("judge", ""),
                status=case_data.get("status", "Listed"),
                highlighted=highlighted
            ))
        
        db.commit()
        
        # Generate PDF in background
        pdf_generator = PDFGenerator()
        pdf_path = await pdf_generator.generate_cause_list_pdf(
            court_type=request.court_type,
            date=request.date,
            entries=entries
        )
        
        # Update database with PDF path
        if pdf_path:
            db.query(CauseList).filter(
                CauseList.court_type == request.court_type,
                CauseList.date == request.date
            ).update({"pdf_path": pdf_path})
            db.commit()
        
        return CauseListResponse(
            court_type=request.court_type,
            date=request.date,
            entries=entries,
            pdf_url=f"/static/pdfs/{pdf_path}" if pdf_path else None,
            total_cases=len(entries)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cause list: {str(e)}")

@router.get("/download-judgment")
async def download_judgment(
    case_id: int,
    db: Session = Depends(get_db)
):
    """
    Download judgment PDF for a specific case
    """
    try:
        case = db.query(CaseQuery).filter(CaseQuery.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        if not case.judgment_url:
            raise HTTPException(status_code=404, detail="Judgment not available for this case")
        
        # TODO: Implement judgment PDF download
        # This would typically involve downloading from the court website
        # and serving the file
        
        raise HTTPException(status_code=501, detail="Judgment download not implemented yet")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download judgment: {str(e)}")

@router.get("/download-causelist")
async def download_cause_list_pdf(
    court_type: str,
    date: str,
    db: Session = Depends(get_db)
):
    """
    Download cause list PDF for a specific date and court
    """
    try:
        cause_list_entry = db.query(CauseList).filter(
            CauseList.court_type == court_type,
            CauseList.date == date
        ).first()
        
        if not cause_list_entry or not cause_list_entry.pdf_path:
            raise HTTPException(status_code=404, detail="Cause list PDF not found")
        
        return FileResponse(
            path=cause_list_entry.pdf_path,
            filename=f"causelist_{court_type}_{date}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download cause list: {str(e)}")

@router.get("/cause-list", response_model=List[CauseListEntry])
async def get_cause_list(limit: int = 10, db: Session = Depends(get_db)):
    """Get cause list entries"""
    try:
        # Return demo cause list data
        demo_data = demo_service.get_cause_list("high_court", "2024-10-03")
        result = []
        for entry in demo_data[:limit]:
            result.append(CauseListEntry(
                sr_no=entry["sr_no"],
                case_number=entry["case_number"],
                parties=entry["parties"],
                hearing_type=entry["hearing_type"],
                time=entry["time"],
                court_room=entry["court_room"],
                judge=entry["judge"],
                status=entry["status"],
                highlighted=False
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cause list: {str(e)}")

@router.get("/recent-searches", response_model=List[CaseQueryResponse])
async def get_recent_searches(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent case searches
    """
    try:
        recent_cases = db.query(CaseQuery).order_by(
            CaseQuery.created_at.desc()
        ).limit(limit).all()
        
        results = []
        for case in recent_cases:
            results.append(CaseQueryResponse(
                id=case.id,
                case_type=case.case_type,
                case_number=case.case_number,
                year=case.year,
                court_type=case.court_type,
                details=CaseDetails(
                    parties=case.parties,
                    filing_date=case.filing_date,
                    next_hearing_date=case.next_hearing_date,
                    case_status=case.case_status,
                    judgment_url=case.judgment_url
                ),
                success=case.success,
                error_message=case.error_message,
                created_at=case.created_at
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent searches: {str(e)}")

# Advanced Cause List Management Endpoints

@router.post("/cause-list/auto-update")
async def auto_update_cause_lists(
    court_types: List[str] = ["high_court", "district_court"],
    date_range: int = 7,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Automatically fetch and update cause lists from court websites
    """
    try:
        cause_list_manager = CauseListManager()
        
        # Run update in background
        background_tasks.add_task(
            cause_list_manager.fetch_and_update_cause_lists,
            db, court_types, date_range
        )
        
        return {
            "message": "Cause list update initiated",
            "court_types": court_types,
            "date_range": date_range,
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate cause list update: {str(e)}")

@router.get("/cause-list/filtered")
async def get_filtered_cause_list(
    court_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    case_number: Optional[str] = None,
    judge: Optional[str] = None,
    status: Optional[str] = None,
    hearing_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get cause list with advanced filtering options
    """
    try:
        from datetime import datetime
        
        # Parse dates
        date_from_parsed = None
        date_to_parsed = None
        
        if date_from:
            date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
        if date_to:
            date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
        
        # Create filter
        filters = CauseListFilter(
            court_type=court_type,
            date_from=date_from_parsed,
            date_to=date_to_parsed,
            case_number=case_number,
            judge=judge,
            status=status,
            hearing_type=hearing_type
        )
        
        cause_list_manager = CauseListManager()
        entries = await cause_list_manager.get_filtered_cause_list(
            db, filters, limit, offset
        )
        
        # Convert to response format
        result = []
        for entry in entries:
            result.append({
                "id": entry.id,
                "sr_no": entry.sr_no,
                "case_number": entry.case_number,
                "parties": entry.parties,
                "hearing_type": entry.hearing_type,
                "time": entry.time,
                "court_room": entry.court_room,
                "judge": entry.judge,
                "status": entry.status,
                "date": entry.date.isoformat(),
                "court_type": entry.court_type
            })
        
        return {
            "entries": result,
            "total_found": len(result),
            "filters_applied": {
                "court_type": court_type,
                "date_from": date_from,
                "date_to": date_to,
                "case_number": case_number,
                "judge": judge,
                "status": status,
                "hearing_type": hearing_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get filtered cause list: {str(e)}")

@router.get("/case/{case_number}/status-history")
async def get_case_status_history(
    case_number: str,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Track status changes for a specific case over time
    """
    try:
        cause_list_manager = CauseListManager()
        status_changes = await cause_list_manager.track_case_status_changes(
            db, case_number, days_back
        )
        
        return {
            "case_number": case_number,
            "days_back": days_back,
            "status_changes": [
                {
                    "case_number": change.case_number,
                    "old_status": change.old_status,
                    "new_status": change.new_status,
                    "updated_at": change.updated_at.isoformat(),
                    "next_hearing_date": change.next_hearing_date.isoformat() if change.next_hearing_date else None
                }
                for change in status_changes
            ],
            "total_changes": len(status_changes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get case status history: {str(e)}")

@router.get("/cause-list/report")
async def generate_cause_list_report(
    court_type: str,
    date_from: str,
    date_to: str,
    include_statistics: bool = True,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive cause list report with statistics
    """
    try:
        from datetime import datetime
        
        date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
        date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
        
        cause_list_manager = CauseListManager()
        report = await cause_list_manager.generate_cause_list_report(
            db, court_type, date_from_parsed, date_to_parsed, include_statistics
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cause list report: {str(e)}")

@router.post("/notifications/hearing-reminders")
async def schedule_hearing_reminders(
    days_ahead: int = 1,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Schedule reminders for upcoming hearings
    """
    try:
        cause_list_manager = CauseListManager()
        
        # Run reminder scheduling in background
        background_tasks.add_task(
            cause_list_manager.schedule_hearing_reminders,
            db, days_ahead
        )
        
        return {
            "message": "Hearing reminders scheduling initiated",
            "days_ahead": days_ahead,
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule hearing reminders: {str(e)}")

@router.get("/cause-list/export-pdf")
async def export_cause_list_pdf(
    court_type: str,
    date: str,
    include_stats: bool = True,
    db: Session = Depends(get_db)
):
    """
    Export cause list as PDF with enhanced formatting
    """
    try:
        from datetime import datetime
        
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        cause_list_manager = CauseListManager()
        pdf_path = await cause_list_manager.export_cause_list_pdf(
            db, court_type, target_date, include_stats
        )
        
        return {
            "pdf_path": pdf_path,
            "download_url": f"/static/pdfs/{pdf_path}",
            "court_type": court_type,
            "date": date,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export cause list PDF: {str(e)}")

@router.get("/cause-list/statistics")
async def get_cause_list_statistics(
    court_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get cause list statistics and analytics
    """
    try:
        from datetime import datetime, timedelta
        
        # Default to last 30 days if no dates provided
        if not date_from:
            date_from = (datetime.now().date() - timedelta(days=30)).isoformat()
        if not date_to:
            date_to = datetime.now().date().isoformat()
        
        date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
        date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
        
        cause_list_manager = CauseListManager()
        report = await cause_list_manager.generate_cause_list_report(
            db, court_type or "all", date_from_parsed, date_to_parsed, True
        )
        
        return {
            "statistics": report.get("statistics", {}),
            "total_cases": report.get("total_cases", 0),
            "date_range": {
                "from": date_from,
                "to": date_to
            },
            "court_type": court_type or "all"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cause list statistics: {str(e)}")