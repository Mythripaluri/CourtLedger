"""
n8n Integration Router
Enhanced API endpoints for n8n workflow automation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from ..services.n8n_workflow_manager import N8NWorkflowManager
from ..services.notification_service import NotificationService
from ..services.cause_list_manager import CauseListManager
from ..database import CaseQuery, CauseList, DriveCommandLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/n8n", tags=["n8n Integration"])

# Initialize services
notification_service = NotificationService()
cause_list_manager = CauseListManager()

@router.get("/health")
async def n8n_health_check():
    """Check n8n service health and connectivity"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            health_status = await n8n_manager._check_n8n_health()
            
            return {
                "status": "healthy" if health_status.get('healthy') else "unhealthy",
                "n8n_version": health_status.get('version'),
                "timestamp": datetime.now().isoformat(),
                "available_triggers": len(n8n_manager.get_available_triggers()),
                "workflows_configured": len(n8n_manager.workflows)
            }
    except Exception as e:
        logger.error(f"n8n health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"n8n service unavailable: {str(e)}")

@router.post("/setup")
async def setup_n8n_instance():
    """Setup and configure n8n instance with all workflows"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            setup_result = await n8n_manager.setup_n8n_instance()
            
            if setup_result['success']:
                return {
                    "status": "success",
                    "message": "n8n instance setup completed successfully",
                    "workflows_deployed": setup_result['workflows_deployed'],
                    "webhook_endpoints": setup_result['webhook_endpoints'],
                    "deployment_results": setup_result['deployment_results']
                }
            else:
                return {
                    "status": "failed",
                    "error": setup_result['error'],
                    "setup_instructions": setup_result.get('setup_instructions')
                }
                
    except Exception as e:
        logger.error(f"n8n setup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

@router.get("/workflows/status")
async def get_workflow_status():
    """Get status of all n8n workflows"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            status = await n8n_manager.get_workflow_status()
            
            if status['success']:
                return {
                    "status": "success",
                    "total_workflows": status['total_workflows'],
                    "active_workflows": status['active_workflows'],
                    "workflows": status['workflows']
                }
            else:
                raise HTTPException(status_code=503, detail=status['error'])
                
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/triggers")
async def get_available_triggers():
    """Get all available workflow triggers and their configurations"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            triggers = n8n_manager.get_available_triggers()
            
            return {
                "status": "success",
                "triggers": {
                    name: {
                        "webhook_url": trigger.webhook_url,
                        "workflow_name": trigger.workflow_name,
                        "trigger_type": trigger.trigger_type,
                        "payload_schema": trigger.payload_schema,
                        "active": trigger.active
                    }
                    for name, trigger in triggers.items()
                }
            }
            
    except Exception as e:
        logger.error(f"Error getting triggers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger/court-update")
async def trigger_court_update_notification(
    case_number: str,
    message: str,
    phone_number: str,
    additional_data: Optional[Dict[str, Any]] = None
):
    """Trigger court update notification workflow"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            execution = await n8n_manager.send_court_update_notification(
                case_number=case_number,
                message=message,
                phone_number=phone_number,
                additional_data=additional_data
            )
            
            return {
                "status": "success",
                "execution_id": execution.execution_id,
                "workflow_status": execution.status,
                "started_at": execution.started_at.isoformat(),
                "case_number": case_number
            }
            
    except Exception as e:
        logger.error(f"Error triggering court update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger/document-backup")
async def trigger_document_backup(
    case_number: str,
    document_type: str,
    file_content: str,
    folder_id: Optional[str] = None
):
    """Trigger document backup to Google Drive workflow"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            execution = await n8n_manager.backup_document_to_drive(
                case_number=case_number,
                document_type=document_type,
                file_content=file_content,
                folder_id=folder_id
            )
            
            return {
                "status": "success",
                "execution_id": execution.execution_id,
                "workflow_status": execution.status,
                "started_at": execution.started_at.isoformat(),
                "case_number": case_number,
                "document_type": document_type
            }
            
    except Exception as e:
        logger.error(f"Error triggering document backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger/calendar-event")
async def trigger_calendar_event_creation(
    case_number: str,
    parties: str,
    hearing_datetime: str,
    court_name: str,
    additional_info: Optional[Dict[str, Any]] = None
):
    """Trigger calendar event creation workflow"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            execution = await n8n_manager.create_calendar_event(
                case_number=case_number,
                parties=parties,
                hearing_datetime=hearing_datetime,
                court_name=court_name,
                additional_info=additional_info
            )
            
            return {
                "status": "success",
                "execution_id": execution.execution_id,
                "workflow_status": execution.status,
                "started_at": execution.started_at.isoformat(),
                "case_number": case_number,
                "hearing_datetime": hearing_datetime
            }
            
    except Exception as e:
        logger.error(f"Error triggering calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger/hearing-reminder")
async def trigger_hearing_reminder(
    case_number: str,
    hearing_date: str,
    hearing_time: str,
    court_name: str,
    phone_number: str
):
    """Trigger hearing reminder workflow"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            execution = await n8n_manager.send_hearing_reminder(
                case_number=case_number,
                hearing_date=hearing_date,
                hearing_time=hearing_time,
                court_name=court_name,
                phone_number=phone_number
            )
            
            return {
                "status": "success",
                "execution_id": execution.execution_id,
                "workflow_status": execution.status,
                "started_at": execution.started_at.isoformat(),
                "case_number": case_number
            }
            
    except Exception as e:
        logger.error(f"Error triggering hearing reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/daily-notifications")
async def trigger_daily_notifications():
    """Manually trigger daily notification workflow"""
    try:
        # Get today's statistics
        today = datetime.now().date()
        statistics = await cause_list_manager.get_statistics()
        
        # Format daily summary
        summary = {
            "date": today.isoformat(),
            "pending_cases": statistics.get("total_pending", 0),
            "todays_hearings": statistics.get("today_hearings", 0),
            "status_changes": statistics.get("recent_changes", 0),
            "urgent_matters": statistics.get("urgent_count", 0)
        }
        
        async with N8NWorkflowManager() as n8n_manager:
            execution = await n8n_manager.trigger_workflow(
                'daily-notifications',
                summary
            )
            
            return {
                "status": "success",
                "execution_id": execution.execution_id,
                "daily_summary": summary,
                "triggered_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error triggering daily notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/auto-update")
async def trigger_auto_update():
    """Manually trigger automated cause list updates"""
    try:
        # Trigger cause list auto-update
        update_result = await cause_list_manager.auto_update_cause_lists(
            court_types=["high_court", "district_court"],
            date_range=3
        )
        
        # If there are status changes, trigger notifications
        if update_result.get("status_changes"):
            async with N8NWorkflowManager() as n8n_manager:
                for change in update_result["status_changes"]:
                    await n8n_manager.send_court_update_notification(
                        case_number=change["case_number"],
                        message=f"Status updated: {change['old_status']} → {change['new_status']}",
                        phone_number="919876543210",
                        additional_data={
                            "change_type": "status_update",
                            "old_status": change["old_status"],
                            "new_status": change["new_status"]
                        }
                    )
        
        return {
            "status": "success",
            "updates_processed": update_result.get("processed_count", 0),
            "status_changes": len(update_result.get("status_changes", [])),
            "notifications_sent": len(update_result.get("status_changes", [])),
            "triggered_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering auto-update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/backup-all-documents")
async def trigger_bulk_document_backup():
    """Trigger bulk backup of all recent documents"""
    try:
        # Get recent cause list entries that need backup
        recent_entries = await cause_list_manager.get_recent_entries(days=7)
        
        backup_results = []
        
        async with N8NWorkflowManager() as n8n_manager:
            for entry in recent_entries[:10]:  # Limit to 10 for demo
                try:
                    execution = await n8n_manager.backup_document_to_drive(
                        case_number=entry.get("case_number", "Unknown"),
                        document_type="cause_list_entry",
                        file_content=str(entry),  # In real scenario, this would be PDF content
                        folder_id=None
                    )
                    
                    backup_results.append({
                        "case_number": entry.get("case_number"),
                        "status": execution.status,
                        "execution_id": execution.execution_id
                    })
                    
                except Exception as backup_error:
                    logger.error(f"Error backing up {entry.get('case_number')}: {backup_error}")
                    backup_results.append({
                        "case_number": entry.get("case_number"),
                        "status": "error",
                        "error": str(backup_error)
                    })
        
        return {
            "status": "success",
            "total_backups_attempted": len(backup_results),
            "successful_backups": len([r for r in backup_results if r["status"] == "success"]),
            "failed_backups": len([r for r in backup_results if r["status"] == "error"]),
            "backup_results": backup_results,
            "triggered_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering bulk backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automation/monitoring-summary")
async def get_monitoring_summary():
    """Get comprehensive monitoring summary for n8n workflows"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            # Get workflow status
            workflow_status = await n8n_manager.get_workflow_status()
            
            # Get system health
            health_status = await n8n_manager._check_n8n_health()
            
            # Get recent statistics
            statistics = await cause_list_manager.get_statistics()
            
            monitoring_summary = {
                "timestamp": datetime.now().isoformat(),
                "system_health": {
                    "n8n_healthy": health_status.get('healthy', False),
                    "n8n_version": health_status.get('version'),
                    "workflows_active": workflow_status.get('active_workflows', 0) if workflow_status.get('success') else 0,
                    "total_workflows": workflow_status.get('total_workflows', 0) if workflow_status.get('success') else 0
                },
                "court_statistics": {
                    "total_cases": statistics.get("total_cases", 0),
                    "pending_cases": statistics.get("total_pending", 0),
                    "today_hearings": statistics.get("today_hearings", 0),
                    "recent_updates": statistics.get("recent_changes", 0)
                },
                "automation_status": {
                    "last_daily_notification": "Manual trigger required",
                    "last_auto_update": "Manual trigger required",
                    "last_bulk_backup": "Manual trigger required"
                },
                "recommendations": []
            }
            
            # Generate recommendations
            if not monitoring_summary["system_health"]["n8n_healthy"]:
                monitoring_summary["recommendations"].append("n8n service needs attention - check connectivity")
            
            if monitoring_summary["system_health"]["workflows_active"] == 0:
                monitoring_summary["recommendations"].append("No active workflows - run setup to deploy workflows")
            
            if monitoring_summary["court_statistics"]["today_hearings"] > 10:
                monitoring_summary["recommendations"].append("High hearing volume today - ensure calendar events are created")
            
            if monitoring_summary["court_statistics"]["recent_updates"] > 5:
                monitoring_summary["recommendations"].append("Multiple recent updates - consider sending summary notifications")
            
            return monitoring_summary
            
    except Exception as e:
        logger.error(f"Error getting monitoring summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/webhook/{trigger_name}")
async def test_webhook_trigger(trigger_name: str, test_data: Dict[str, Any]):
    """Test webhook trigger with sample data"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            execution = await n8n_manager.trigger_workflow(trigger_name, test_data)
            
            return {
                "status": "success",
                "test_trigger": trigger_name,
                "execution_id": execution.execution_id,
                "workflow_status": execution.status,
                "test_data": test_data,
                "executed_at": execution.started_at.isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error testing webhook trigger {trigger_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config/docker-compose")
async def get_docker_compose_config():
    """Get Docker Compose configuration for n8n setup"""
    try:
        async with N8NWorkflowManager() as n8n_manager:
            setup_instructions = n8n_manager._get_setup_instructions()
            
            return {
                "status": "success",
                "docker_compose": setup_instructions["docker_compose"],
                "manual_setup": setup_instructions["manual_setup"],
                "required_credentials": setup_instructions["required_credentials"]
            }
            
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))