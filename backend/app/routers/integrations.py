from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db, CaseQuery
from ..schemas import (
    GoogleAuthResponse, IntegrationStatus, CalendarEventRequest,
    ErrorResponse
)
from ..services.google_auth import GoogleAuthService
from ..services.calendar_service import GoogleCalendarService

router = APIRouter()

@router.get("/status")
async def get_integration_status(db: Session = Depends(get_db)):
    """
    Get status of all integrations
    """
    try:
        # TODO: Implement actual status checking
        return [
            IntegrationStatus(
                service="google_drive",
                connected=False,
                error="Not configured"
            ),
            IntegrationStatus(
                service="google_calendar",
                connected=False,
                error="Not configured"
            ),
            IntegrationStatus(
                service="n8n",
                connected=False,
                error="Not configured"
            )
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get integration status: {str(e)}")

@router.get("/google/login", response_model=GoogleAuthResponse)
async def google_login_url():
    """Get Google OAuth2 login URL"""
    return await google_auth_url()

@router.get("/google/auth", response_model=GoogleAuthResponse)
async def google_auth_url():
    """
    Get Google OAuth2 authorization URL
    """
    try:
        auth_service = GoogleAuthService()
        auth_url, state = auth_service.get_authorization_url()
        
        return GoogleAuthResponse(
            auth_url=auth_url,
            state=state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@router.get("/google/callback")
async def google_auth_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None
):
    """
    Handle Google OAuth2 callback
    """
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        auth_service = GoogleAuthService()
        credentials = await auth_service.exchange_code_for_token(code, state)
        
        if credentials:
            # TODO: Store credentials securely
            return {"status": "success", "message": "Google integration connected successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete OAuth: {str(e)}")

@router.post("/google-calendar/create-event")
async def create_calendar_event(
    request: CalendarEventRequest,
    db: Session = Depends(get_db)
):
    """
    Create Google Calendar event for case hearing
    """
    try:
        # Get case details
        case = db.query(CaseQuery).filter(CaseQuery.id == request.case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Initialize calendar service
        calendar_service = GoogleCalendarService()
        
        # Create event
        event_data = {
            "summary": request.title or f"Court Hearing - {case.case_number}",
            "description": request.description or f"Case: {case.case_number}\nParties: {case.parties}\nStatus: {case.case_status}",
            "start": {
                "dateTime": request.start_time.isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "end": {
                "dateTime": request.end_time.isoformat(),
                "timeZone": "Asia/Kolkata"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},  # 1 day before
                    {"method": "popup", "minutes": 60}        # 1 hour before
                ]
            }
        }
        
        event = await calendar_service.create_event(event_data)
        
        if event:
            return {
                "status": "success",
                "message": "Calendar event created successfully",
                "event_id": event.get("id"),
                "event_link": event.get("htmlLink")
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create calendar event")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {str(e)}")

@router.get("/google-calendar/events")
async def list_calendar_events(
    start_date: str = None,
    end_date: str = None,
    max_results: int = 10
):
    """
    List upcoming calendar events
    """
    try:
        calendar_service = GoogleCalendarService()
        events = await calendar_service.list_events(
            start_date=start_date,
            end_date=end_date,
            max_results=max_results
        )
        
        return {
            "events": events,
            "total_events": len(events)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list calendar events: {str(e)}")

@router.delete("/google-calendar/event/{event_id}")
async def delete_calendar_event(event_id: str):
    """
    Delete a calendar event
    """
    try:
        calendar_service = GoogleCalendarService()
        result = await calendar_service.delete_event(event_id)
        
        if result:
            return {"status": "success", "message": "Calendar event deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Event not found or could not be deleted")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete calendar event: {str(e)}")

@router.post("/n8n/webhook")
async def n8n_webhook_handler(request: Request):
    """
    Handle n8n webhook for workflow automation
    """
    try:
        data = await request.json()
        
        # TODO: Implement n8n workflow handling
        # This would process different types of automation triggers
        # such as:
        # - New case filing notifications
        # - Hearing date reminders
        # - Document processing workflows
        # - Integration with other services
        
        return {
            "status": "success",
            "message": "n8n webhook processed successfully",
            "received_data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process n8n webhook: {str(e)}")

@router.get("/n8n/workflows")
async def list_n8n_workflows():
    """
    List available n8n workflows
    """
    try:
        # TODO: Implement n8n API integration to list workflows
        workflows = [
            {
                "id": "court_case_reminder",
                "name": "Court Case Hearing Reminder",
                "description": "Sends WhatsApp reminders for upcoming court hearings",
                "active": False
            },
            {
                "id": "document_backup",
                "name": "Document Backup to Drive",
                "description": "Automatically backup case documents to Google Drive",
                "active": False
            },
            {
                "id": "causelist_notification",
                "name": "Daily Cause List Notification",
                "description": "Daily WhatsApp notification of cause list updates",
                "active": False
            }
        ]
        
        return {
            "workflows": workflows,
            "total_workflows": len(workflows)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list n8n workflows: {str(e)}")

@router.post("/n8n/workflow/{workflow_id}/activate")
async def activate_n8n_workflow(workflow_id: str):
    """
    Activate an n8n workflow
    """
    try:
        # TODO: Implement n8n API call to activate workflow
        return {
            "status": "success",
            "message": f"Workflow {workflow_id} activated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate workflow: {str(e)}")

@router.post("/n8n/workflow/{workflow_id}/deactivate")
async def deactivate_n8n_workflow(workflow_id: str):
    """
    Deactivate an n8n workflow
    """
    try:
        # TODO: Implement n8n API call to deactivate workflow
        return {
            "status": "success",
            "message": f"Workflow {workflow_id} deactivated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate workflow: {str(e)}")