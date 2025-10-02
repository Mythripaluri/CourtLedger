from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
import asyncio
import logging
from dataclasses import dataclass

from ..database import CauseList, CaseQuery
from ..services.court_scraper import CourtScraper
from ..services.pdf_generator import PDFGenerator
from ..services.notification_service import NotificationService
from ..config import settings

logger = logging.getLogger(__name__)

@dataclass
class CauseListFilter:
    """Filter criteria for cause list queries"""
    court_type: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    case_number: Optional[str] = None
    judge: Optional[str] = None
    status: Optional[str] = None
    hearing_type: Optional[str] = None

@dataclass
class CaseStatusUpdate:
    """Case status update information"""
    case_number: str
    old_status: str
    new_status: str
    updated_at: datetime
    next_hearing_date: Optional[date] = None

class CauseListManager:
    """
    Advanced Cause List Management System
    
    Features:
    - Automated cause list fetching from court websites
    - Date-based filtering and search
    - Case status tracking and updates
    - Notification system for case hearings
    - PDF generation for cause lists
    - Integration with calendar for reminders
    """
    
    def __init__(self):
        self.scraper = CourtScraper()
        self.pdf_generator = PDFGenerator()
        self.notification_service = NotificationService()
        
    async def fetch_and_update_cause_lists(
        self, 
        db: Session,
        court_types: List[str] = ["high_court", "district_court"],
        date_range: int = 7  # days
    ) -> Dict[str, Any]:
        """
        Automated cause list fetching for multiple dates and courts
        """
        results = {
            "success": [],
            "errors": [],
            "updates": [],
            "new_cases": 0,
            "status_changes": []
        }
        
        start_date = datetime.now().date()
        dates_to_fetch = [
            start_date + timedelta(days=i) 
            for i in range(date_range)
        ]
        
        for court_type in court_types:
            for target_date in dates_to_fetch:
                try:
                    # Fetch cause list from court website
                    if court_type == "high_court":
                        cause_list_data = await self.scraper.scrape_high_court_causelist(
                            target_date.strftime("%Y-%m-%d")
                        )
                    else:
                        cause_list_data = await self.scraper.scrape_district_court_causelist(
                            target_date.strftime("%Y-%m-%d")
                        )
                    
                    # Process and update database
                    update_result = await self._process_cause_list_data(
                        db, court_type, target_date, cause_list_data
                    )
                    
                    results["success"].append({
                        "court_type": court_type,
                        "date": target_date.isoformat(),
                        "cases_found": len(cause_list_data),
                        "new_cases": update_result["new_cases"],
                        "updates": update_result["updates"]
                    })
                    
                    results["new_cases"] += update_result["new_cases"]
                    results["status_changes"].extend(update_result["status_changes"])
                    
                except Exception as e:
                    logger.error(f"Error fetching cause list for {court_type} on {target_date}: {e}")
                    results["errors"].append({
                        "court_type": court_type,
                        "date": target_date.isoformat(),
                        "error": str(e)
                    })
                    
                # Add delay to avoid overwhelming court websites
                await asyncio.sleep(2)
        
        return results
    
    async def _process_cause_list_data(
        self,
        db: Session,
        court_type: str,
        target_date: date,
        cause_list_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process and update cause list data in database"""
        
        result = {
            "new_cases": 0,
            "updates": 0,
            "status_changes": []
        }
        
        for i, case_data in enumerate(cause_list_data):
            case_number = case_data.get("case_number", "")
            
            # Check if case already exists for this date
            existing = db.query(CauseList).filter(
                CauseList.court_type == court_type,
                CauseList.date == target_date,
                CauseList.case_number == case_number
            ).first()
            
            if existing:
                # Check for status changes
                old_status = existing.status
                new_status = case_data.get("status", "Listed")
                
                if old_status != new_status:
                    existing.status = new_status
                    existing.updated_at = datetime.now()
                    
                    # Track status change
                    status_change = CaseStatusUpdate(
                        case_number=case_number,
                        old_status=old_status,
                        new_status=new_status,
                        updated_at=datetime.now(),
                        next_hearing_date=existing.date
                    )
                    result["status_changes"].append(status_change)
                    result["updates"] += 1
                    
                    # Send notification for important status changes
                    if new_status in ["Disposed", "Adjourned", "Part Heard"]:
                        await self.notification_service.notify_status_change(
                            case_number, old_status, new_status, target_date
                        )
                
                # Update other fields
                existing.parties = case_data.get("parties", existing.parties)
                existing.hearing_type = case_data.get("hearing_type", existing.hearing_type)
                existing.time = case_data.get("time", existing.time)
                existing.court_room = case_data.get("court_room", existing.court_room)
                existing.judge = case_data.get("judge", existing.judge)
                
            else:
                # Create new cause list entry
                cause_list = CauseList(
                    court_type=court_type,
                    date=target_date,
                    case_number=case_number,
                    sr_no=i + 1,
                    parties=case_data.get("parties", ""),
                    hearing_type=case_data.get("hearing_type", ""),
                    time=case_data.get("time", ""),
                    court_room=case_data.get("court_room", ""),
                    judge=case_data.get("judge", ""),
                    status=case_data.get("status", "Listed"),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(cause_list)
                result["new_cases"] += 1
        
        db.commit()
        return result
    
    async def get_filtered_cause_list(
        self,
        db: Session,
        filters: CauseListFilter,
        limit: int = 100,
        offset: int = 0
    ) -> List[CauseList]:
        """
        Get cause list with advanced filtering
        """
        query = db.query(CauseList)
        
        if filters.court_type:
            query = query.filter(CauseList.court_type == filters.court_type)
            
        if filters.date_from:
            query = query.filter(CauseList.date >= filters.date_from)
            
        if filters.date_to:
            query = query.filter(CauseList.date <= filters.date_to)
            
        if filters.case_number:
            query = query.filter(
                CauseList.case_number.ilike(f"%{filters.case_number}%")
            )
            
        if filters.judge:
            query = query.filter(
                CauseList.judge.ilike(f"%{filters.judge}%")
            )
            
        if filters.status:
            query = query.filter(CauseList.status == filters.status)
            
        if filters.hearing_type:
            query = query.filter(CauseList.hearing_type == filters.hearing_type)
        
        return query.order_by(
            CauseList.date.desc(),
            CauseList.sr_no.asc()
        ).offset(offset).limit(limit).all()
    
    async def track_case_status_changes(
        self,
        db: Session,
        case_number: str,
        days_back: int = 30
    ) -> List[CaseStatusUpdate]:
        """
        Track status changes for a specific case over time
        """
        cutoff_date = datetime.now().date() - timedelta(days=days_back)
        
        # Get all entries for this case within the time period
        entries = db.query(CauseList).filter(
            CauseList.case_number.ilike(f"%{case_number}%"),
            CauseList.date >= cutoff_date
        ).order_by(CauseList.date.asc()).all()
        
        status_changes = []
        previous_status = None
        
        for entry in entries:
            if previous_status and previous_status != entry.status:
                status_changes.append(CaseStatusUpdate(
                    case_number=entry.case_number,
                    old_status=previous_status,
                    new_status=entry.status,
                    updated_at=entry.updated_at or datetime.now(),
                    next_hearing_date=entry.date
                ))
            previous_status = entry.status
        
        return status_changes
    
    async def generate_cause_list_report(
        self,
        db: Session,
        court_type: str,
        date_from: date,
        date_to: date,
        include_statistics: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive cause list report with statistics
        """
        entries = await self.get_filtered_cause_list(
            db,
            CauseListFilter(
                court_type=court_type,
                date_from=date_from,
                date_to=date_to
            ),
            limit=1000
        )
        
        report = {
            "court_type": court_type,
            "date_range": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "total_cases": len(entries),
            "entries": entries
        }
        
        if include_statistics:
            # Calculate statistics
            status_counts = {}
            hearing_type_counts = {}
            judge_counts = {}
            daily_counts = {}
            
            for entry in entries:
                # Status distribution
                status = entry.status or "Unknown"
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Hearing type distribution
                hearing_type = entry.hearing_type or "Unknown"
                hearing_type_counts[hearing_type] = hearing_type_counts.get(hearing_type, 0) + 1
                
                # Judge workload
                judge = entry.judge or "Unknown"
                judge_counts[judge] = judge_counts.get(judge, 0) + 1
                
                # Daily case counts
                date_str = entry.date.isoformat() if hasattr(entry.date, 'isoformat') else str(entry.date)
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
            
            report["statistics"] = {
                "status_distribution": status_counts,
                "hearing_type_distribution": hearing_type_counts,
                "judge_workload": judge_counts,
                "daily_case_counts": daily_counts
            }
        
        return report
    
    async def schedule_hearing_reminders(
        self,
        db: Session,
        days_ahead: int = 1
    ) -> Dict[str, Any]:
        """
        Schedule reminders for upcoming hearings
        """
        reminder_date = datetime.now().date() + timedelta(days=days_ahead)
        
        upcoming_hearings = db.query(CauseList).filter(
            CauseList.date == reminder_date,
            CauseList.status.in_(["Listed", "Part Heard", "Adjourned"])
        ).all()
        
        reminders_sent = 0
        errors = []
        
        for hearing in upcoming_hearings:
            try:
                await self.notification_service.send_hearing_reminder(
                    case_number=hearing.case_number,
                    parties=hearing.parties,
                    hearing_date=hearing.date,
                    hearing_time=hearing.time,
                    court_room=hearing.court_room,
                    judge=hearing.judge
                )
                reminders_sent += 1
                
            except Exception as e:
                logger.error(f"Failed to send reminder for {hearing.case_number}: {e}")
                errors.append({
                    "case_number": hearing.case_number,
                    "error": str(e)
                })
        
        return {
            "reminder_date": reminder_date.isoformat(),
            "total_hearings": len(upcoming_hearings),
            "reminders_sent": reminders_sent,
            "errors": errors
        }
    
    async def export_cause_list_pdf(
        self,
        db: Session,
        court_type: str,
        target_date: date,
        include_stats: bool = True
    ) -> str:
        """
        Export cause list as PDF with enhanced formatting
        """
        entries = await self.get_filtered_cause_list(
            db,
            CauseListFilter(
                court_type=court_type,
                date_from=target_date,
                date_to=target_date
            )
        )
        
        # Convert to format expected by PDF generator
        pdf_entries = []
        for entry in entries:
            pdf_entries.append({
                "sr_no": entry.sr_no,
                "case_number": entry.case_number,
                "parties": entry.parties,
                "hearing_type": entry.hearing_type,
                "time": entry.time,
                "court_room": entry.court_room,
                "judge": entry.judge,
                "status": entry.status
            })
        
        pdf_path = await self.pdf_generator.generate_cause_list_pdf(
            court_type=court_type,
            date=target_date.strftime("%Y-%m-%d"),
            entries=pdf_entries
        )
        
        # Update database with PDF path
        db.query(CauseList).filter(
            CauseList.court_type == court_type,
            CauseList.date == target_date
        ).update({"pdf_path": pdf_path})
        db.commit()
        
        return pdf_path

    def filter_cause_list(self, entries: List[Any], filters: Dict[str, Any]) -> List[Any]:
        """
        Filter cause list entries based on given criteria
        """
        filtered_entries = entries.copy()
        
        if filters.get("case_type"):
            filtered_entries = [e for e in filtered_entries if filters["case_type"].lower() in e.case_number.lower()]
        
        if filters.get("status"):
            filtered_entries = [e for e in filtered_entries if filters["status"].lower() in e.status.lower()]
        
        if filters.get("date_from"):
            date_from = datetime.strptime(filters["date_from"], "%Y-%m-%d").date()
            filtered_entries = [e for e in filtered_entries if e.date >= date_from]
        
        if filters.get("date_to"):
            date_to = datetime.strptime(filters["date_to"], "%Y-%m-%d").date()
            filtered_entries = [e for e in filtered_entries if e.date <= date_to]
        
        return filtered_entries

    def get_statistics(self, entries: List[Any]) -> Dict[str, Any]:
        """
        Get statistics for cause list entries
        """
        if not entries:
            return {
                "total_cases": 0,
                "by_status": {},
                "by_court_type": {},
                "by_date": {}
            }
        
        stats = {
            "total_cases": len(entries),
            "by_status": {},
            "by_court_type": {},
            "by_date": {}
        }
        
        for entry in entries:
            # Count by status
            status = getattr(entry, 'status', 'unknown')
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by court type
            court_type = getattr(entry, 'court_type', 'unknown')
            stats["by_court_type"][court_type] = stats["by_court_type"].get(court_type, 0) + 1
            
            # Count by date
            date_key = getattr(entry, 'date', 'unknown')
            if hasattr(date_key, 'strftime'):
                date_key = date_key.strftime("%Y-%m-%d")
            stats["by_date"][str(date_key)] = stats["by_date"].get(str(date_key), 0) + 1
        
        return stats