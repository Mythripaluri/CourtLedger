"""
n8n Workflow Automation Service
Complete integration for court case management automation
"""

import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os

from ..config import settings

logger = logging.getLogger(__name__)

@dataclass
class N8NWorkflowTrigger:
    """n8n workflow trigger configuration"""
    webhook_url: str
    workflow_name: str
    trigger_type: str  # 'webhook', 'cron', 'manual'
    payload_schema: Dict[str, Any]
    active: bool = True

@dataclass
class N8NWorkflowExecution:
    """n8n workflow execution result"""
    execution_id: str
    workflow_name: str
    status: str  # 'success', 'error', 'running'
    started_at: datetime
    finished_at: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class N8NWorkflowManager:
    """
    Complete n8n Workflow Automation Manager
    
    Features:
    - n8n instance setup and configuration
    - Webhook triggers for court updates
    - Automated document backup to Drive
    - Daily notification workflows
    - Calendar event automation
    - WhatsApp notification integration
    """
    
    def __init__(self):
        self.n8n_base_url = getattr(settings, 'n8n_base_url', 'http://localhost:5678')
        self.n8n_api_key = getattr(settings, 'n8n_api_key', '')
        self.n8n_webhook_base = getattr(settings, 'n8n_webhook_base', f'{self.n8n_base_url}/webhook')
        
        # Workflow definitions
        self.workflows = self._load_workflow_definitions()
        
        # HTTP session for API calls
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _load_workflow_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load workflow definitions from JSON file"""
        try:
            workflows_file = os.path.join(
                os.path.dirname(__file__), 
                '../../n8n_workflows.json'
            )
            
            if os.path.exists(workflows_file):
                with open(workflows_file, 'r', encoding='utf-8') as f:
                    base_workflow = json.load(f)
                    return {
                        'court_automation': base_workflow,
                        **self._get_additional_workflows()
                    }
            else:
                logger.warning("n8n workflows file not found, using default workflows")
                return self._get_default_workflows()
                
        except Exception as e:
            logger.error(f"Error loading n8n workflows: {e}")
            return self._get_default_workflows()
    
    def _get_additional_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get additional workflow definitions"""
        return {
            'daily_notifications': self._create_daily_notification_workflow(),
            'calendar_automation': self._create_calendar_automation_workflow(),
            'document_processing': self._create_document_processing_workflow(),
            'status_monitoring': self._create_status_monitoring_workflow()
        }
    
    def _get_default_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get default workflow definitions"""
        return {
            'court_automation': self._create_basic_court_workflow(),
            'daily_notifications': self._create_daily_notification_workflow(),
            'calendar_automation': self._create_calendar_automation_workflow(),
            'document_processing': self._create_document_processing_workflow()
        }
    
    def _create_basic_court_workflow(self) -> Dict[str, Any]:
        """Create basic court automation workflow"""
        return {
            "name": "Court Case Automation",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "court-update",
                        "responseMode": "responseNode"
                    },
                    "id": "court-webhook",
                    "name": "Court Update Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "operation": "sendMessage",
                        "chatId": "={{ $json.phone_number }}",
                        "text": "🏛️ Court Update: {{ $json.message }}"
                    },
                    "id": "whatsapp-notify",
                    "name": "WhatsApp Notification",
                    "type": "n8n-nodes-base.whatsApp",
                    "position": [460, 300]
                }
            ],
            "connections": {
                "Court Update Webhook": {
                    "main": [[{"node": "WhatsApp Notification", "type": "main", "index": 0}]]
                }
            }
        }
    
    def _create_daily_notification_workflow(self) -> Dict[str, Any]:
        """Create daily notification workflow"""
        return {
            "name": "Daily Court Notifications",
            "nodes": [
                {
                    "parameters": {"cronExpression": "0 8 * * 1-5"},
                    "id": "daily-cron",
                    "name": "Daily Trigger",
                    "type": "n8n-nodes-base.cron",
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "url": f"{settings.api_base_url}/api/court/cause-list/statistics",
                        "method": "GET"
                    },
                    "id": "fetch-stats",
                    "name": "Fetch Court Statistics",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [460, 300]
                },
                {
                    "parameters": {
                        "url": f"{settings.api_base_url}/api/notifications/daily-summary",
                        "method": "POST",
                        "body": {
                            "date": "{{ new Date().toISOString().split('T')[0] }}",
                            "statistics": "={{ $json }}"
                        }
                    },
                    "id": "send-summary",
                    "name": "Send Daily Summary",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [680, 300]
                }
            ],
            "connections": {
                "Daily Trigger": {
                    "main": [[{"node": "Fetch Court Statistics", "type": "main", "index": 0}]]
                },
                "Fetch Court Statistics": {
                    "main": [[{"node": "Send Daily Summary", "type": "main", "index": 0}]]
                }
            }
        }
    
    def _create_calendar_automation_workflow(self) -> Dict[str, Any]:
        """Create calendar automation workflow"""
        return {
            "name": "Calendar Event Automation",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "calendar-event",
                        "responseMode": "responseNode"
                    },
                    "id": "calendar-webhook",
                    "name": "Calendar Event Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "operation": "create",
                        "calendarId": "primary",
                        "summary": "Court Hearing: {{ $json.case_number }}",
                        "description": "Case: {{ $json.case_number }}\\nParties: {{ $json.parties }}\\nCourt: {{ $json.court_name }}",
                        "start": {
                            "dateTime": "{{ $json.hearing_datetime }}",
                            "timeZone": "Asia/Kolkata"
                        },
                        "reminders": {
                            "useDefault": False,
                            "overrides": [
                                {"method": "email", "minutes": 1440},
                                {"method": "popup", "minutes": 60}
                            ]
                        }
                    },
                    "id": "create-calendar-event",
                    "name": "Create Calendar Event",
                    "type": "n8n-nodes-base.googleCalendar",
                    "position": [460, 300]
                },
                {
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "{\\n  \\\"status\\\": \\\"success\\\",\\n  \\\"event_id\\\": \\\"={{ $json.id }}\\\",\\n  \\\"event_link\\\": \\\"={{ $json.htmlLink }}\\\"\\n}"
                    },
                    "id": "calendar-response",
                    "name": "Calendar Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "position": [680, 300]
                }
            ],
            "connections": {
                "Calendar Event Webhook": {
                    "main": [[{"node": "Create Calendar Event", "type": "main", "index": 0}]]
                },
                "Create Calendar Event": {
                    "main": [[{"node": "Calendar Response", "type": "main", "index": 0}]]
                }
            }
        }
    
    def _create_document_processing_workflow(self) -> Dict[str, Any]:
        """Create document processing workflow"""
        return {
            "name": "Document Processing Automation",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "process-document",
                        "responseMode": "responseNode"
                    },
                    "id": "document-webhook",
                    "name": "Document Processing Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "operation": "upload",
                        "folderId": "={{ $json.folder_id || 'root' }}",
                        "fileName": "{{ $json.case_number }}_{{ $json.document_type }}_{{ new Date().toISOString().split('T')[0] }}.pdf",
                        "fileContent": "={{ $json.file_content }}"
                    },
                    "id": "upload-to-drive",
                    "name": "Upload to Google Drive",
                    "type": "n8n-nodes-base.googleDrive",
                    "position": [460, 300]
                },
                {
                    "parameters": {
                        "url": f"{settings.api_base_url}/api/drive/log-backup",
                        "method": "POST",
                        "body": {
                            "case_number": "={{ $json.case_number }}",
                            "document_type": "={{ $json.document_type }}",
                            "drive_file_id": "={{ $json.id }}",
                            "backup_date": "{{ new Date().toISOString() }}"
                        }
                    },
                    "id": "log-backup",
                    "name": "Log Backup to Database",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [680, 300]
                },
                {
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": "{\\n  \\\"status\\\": \\\"success\\\",\\n  \\\"file_id\\\": \\\"={{ $json.id }}\\\",\\n  \\\"backup_logged\\\": true\\n}"
                    },
                    "id": "document-response",
                    "name": "Document Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "position": [900, 300]
                }
            ],
            "connections": {
                "Document Processing Webhook": {
                    "main": [[{"node": "Upload to Google Drive", "type": "main", "index": 0}]]
                },
                "Upload to Google Drive": {
                    "main": [[{"node": "Log Backup to Database", "type": "main", "index": 0}]]
                },
                "Log Backup to Database": {
                    "main": [[{"node": "Document Response", "type": "main", "index": 0}]]
                }
            }
        }
    
    def _create_status_monitoring_workflow(self) -> Dict[str, Any]:
        """Create status monitoring workflow"""
        return {
            "name": "Court Status Monitoring",
            "nodes": [
                {
                    "parameters": {"cronExpression": "0 */4 * * *"},
                    "id": "monitoring-cron",
                    "name": "Every 4 Hours Trigger",
                    "type": "n8n-nodes-base.cron",
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "url": f"{settings.api_base_url}/api/court/cause-list/auto-update",
                        "method": "POST",
                        "body": {
                            "court_types": ["high_court", "district_court"],
                            "date_range": 3
                        }
                    },
                    "id": "auto-update",
                    "name": "Auto Update Cause Lists",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [460, 300]
                },
                {
                    "parameters": {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{ $json.status_changes.length }}",
                                    "operation": "larger",
                                    "value2": "0"
                                }
                            ]
                        }
                    },
                    "id": "check-changes",
                    "name": "Check for Status Changes",
                    "type": "n8n-nodes-base.if",
                    "position": [680, 300]
                },
                {
                    "parameters": {
                        "url": f"{settings.api_base_url}/api/notifications/status-changes",
                        "method": "POST",
                        "body": "={{ $json }}"
                    },
                    "id": "notify-changes",
                    "name": "Notify Status Changes",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [900, 300]
                }
            ],
            "connections": {
                "Every 4 Hours Trigger": {
                    "main": [[{"node": "Auto Update Cause Lists", "type": "main", "index": 0}]]
                },
                "Auto Update Cause Lists": {
                    "main": [[{"node": "Check for Status Changes", "type": "main", "index": 0}]]
                },
                "Check for Status Changes": {
                    "main": [
                        [{"node": "Notify Status Changes", "type": "main", "index": 0}],
                        []
                    ]
                }
            }
        }
    
    async def setup_n8n_instance(self) -> Dict[str, Any]:
        """Setup and configure n8n instance"""
        try:
            # Check if n8n is running
            health_check = await self._check_n8n_health()
            
            if not health_check['healthy']:
                return {
                    'success': False,
                    'error': 'n8n instance is not running or not accessible',
                    'setup_instructions': self._get_setup_instructions()
                }
            
            # Deploy all workflows
            deployment_results = []
            for workflow_name, workflow_config in self.workflows.items():
                result = await self._deploy_workflow(workflow_name, workflow_config)
                deployment_results.append(result)
            
            # Configure webhook endpoints
            webhook_config = await self._configure_webhooks()
            
            return {
                'success': True,
                'n8n_version': health_check.get('version'),
                'workflows_deployed': len([r for r in deployment_results if r['success']]),
                'webhook_endpoints': webhook_config,
                'deployment_results': deployment_results
            }
            
        except Exception as e:
            logger.error(f"Error setting up n8n instance: {e}")
            return {
                'success': False,
                'error': str(e),
                'setup_instructions': self._get_setup_instructions()
            }
    
    async def _check_n8n_health(self) -> Dict[str, Any]:
        """Check if n8n instance is healthy"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(f"{self.n8n_base_url}/healthz") as response:
                if response.status == 200:
                    data = await response.json()
                    return {'healthy': True, 'version': data.get('version')}
                else:
                    return {'healthy': False, 'status': response.status}
                    
        except Exception as e:
            logger.error(f"n8n health check failed: {e}")
            return {'healthy': False, 'error': str(e)}
    
    async def _deploy_workflow(self, workflow_name: str, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a workflow to n8n"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.n8n_api_key:
                headers['X-N8N-API-KEY'] = self.n8n_api_key
            
            # First, check if workflow exists
            async with self.session.get(
                f"{self.n8n_base_url}/api/v1/workflows",
                headers=headers
            ) as response:
                if response.status == 200:
                    existing_workflows = await response.json()
                    existing_workflow = next(
                        (w for w in existing_workflows.get('data', []) 
                         if w['name'] == workflow_config['name']), 
                        None
                    )
                    
                    if existing_workflow:
                        # Update existing workflow
                        async with self.session.put(
                            f"{self.n8n_base_url}/api/v1/workflows/{existing_workflow['id']}",
                            headers=headers,
                            json=workflow_config
                        ) as update_response:
                            if update_response.status == 200:
                                return {
                                    'success': True,
                                    'workflow_name': workflow_name,
                                    'action': 'updated',
                                    'workflow_id': existing_workflow['id']
                                }
                    else:
                        # Create new workflow
                        async with self.session.post(
                            f"{self.n8n_base_url}/api/v1/workflows",
                            headers=headers,
                            json=workflow_config
                        ) as create_response:
                            if create_response.status == 201:
                                new_workflow = await create_response.json()
                                return {
                                    'success': True,
                                    'workflow_name': workflow_name,
                                    'action': 'created',
                                    'workflow_id': new_workflow['id']
                                }
            
            return {
                'success': False,
                'workflow_name': workflow_name,
                'error': 'Failed to deploy workflow'
            }
            
        except Exception as e:
            logger.error(f"Error deploying workflow {workflow_name}: {e}")
            return {
                'success': False,
                'workflow_name': workflow_name,
                'error': str(e)
            }
    
    async def _configure_webhooks(self) -> Dict[str, str]:
        """Configure webhook endpoints"""
        webhook_endpoints = {
            'court_update': f"{self.n8n_webhook_base}/court-update",
            'document_backup': f"{self.n8n_webhook_base}/document-backup",
            'calendar_event': f"{self.n8n_webhook_base}/calendar-event",
            'process_document': f"{self.n8n_webhook_base}/process-document",
            'hearing_reminder': f"{self.n8n_webhook_base}/court-reminder",
            'causelist_notification': f"{self.n8n_webhook_base}/causelist-notification"
        }
        
        return webhook_endpoints
    
    def _get_setup_instructions(self) -> Dict[str, Any]:
        """Get n8n setup instructions"""
        return {
            'docker_compose': {
                'file': 'docker-compose.n8n.yml',
                'content': '''
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - n8n_data:/home/node/.n8n
      - /var/run/docker.sock:/var/run/docker.sock
volumes:
  n8n_data:
'''
            },
            'manual_setup': [
                '1. Install n8n: npm install n8n -g',
                '2. Start n8n: n8n start',
                '3. Access n8n at http://localhost:5678',
                '4. Configure credentials for WhatsApp, Google Drive, etc.',
                '5. Run the setup_n8n_instance() method to deploy workflows'
            ],
            'required_credentials': [
                'Google Drive API credentials',
                'Google Calendar API credentials', 
                'WhatsApp Business API credentials',
                'SMTP credentials for email notifications'
            ]
        }
    
    async def trigger_workflow(
        self, 
        workflow_trigger: str, 
        payload: Dict[str, Any]
    ) -> N8NWorkflowExecution:
        """Trigger a workflow via webhook"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            webhook_url = f"{self.n8n_webhook_base}/{workflow_trigger}"
            
            async with self.session.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                execution_data = await response.json() if response.content_type == 'application/json' else {}
                
                return N8NWorkflowExecution(
                    execution_id=execution_data.get('executionId', 'unknown'),
                    workflow_name=workflow_trigger,
                    status='success' if response.status == 200 else 'error',
                    started_at=datetime.now(),
                    finished_at=datetime.now(),
                    data=execution_data,
                    error=None if response.status == 200 else f"HTTP {response.status}"
                )
                
        except Exception as e:
            logger.error(f"Error triggering workflow {workflow_trigger}: {e}")
            return N8NWorkflowExecution(
                execution_id='error',
                workflow_name=workflow_trigger,
                status='error',
                started_at=datetime.now(),
                finished_at=datetime.now(),
                error=str(e)
            )
    
    async def send_court_update_notification(
        self,
        case_number: str,
        message: str,
        phone_number: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> N8NWorkflowExecution:
        """Send court update notification via n8n"""
        payload = {
            'case_number': case_number,
            'message': message,
            'phone_number': phone_number,
            'timestamp': datetime.now().isoformat(),
            **(additional_data or {})
        }
        
        return await self.trigger_workflow('court-update', payload)
    
    async def backup_document_to_drive(
        self,
        case_number: str,
        document_type: str,
        file_content: str,
        folder_id: Optional[str] = None
    ) -> N8NWorkflowExecution:
        """Backup document to Google Drive via n8n"""
        payload = {
            'case_number': case_number,
            'document_type': document_type,
            'file_content': file_content,
            'folder_id': folder_id or 'root',
            'timestamp': datetime.now().isoformat()
        }
        
        return await self.trigger_workflow('process-document', payload)
    
    async def create_calendar_event(
        self,
        case_number: str,
        parties: str,
        hearing_datetime: str,
        court_name: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> N8NWorkflowExecution:
        """Create calendar event via n8n"""
        payload = {
            'case_number': case_number,
            'parties': parties,
            'hearing_datetime': hearing_datetime,
            'court_name': court_name,
            'timestamp': datetime.now().isoformat(),
            **(additional_info or {})
        }
        
        return await self.trigger_workflow('calendar-event', payload)
    
    async def send_hearing_reminder(
        self,
        case_number: str,
        hearing_date: str,
        hearing_time: str,
        court_name: str,
        phone_number: str
    ) -> N8NWorkflowExecution:
        """Send hearing reminder via n8n"""
        payload = {
            'case_number': case_number,
            'hearing_date': hearing_date,
            'hearing_time': hearing_time,
            'court_name': court_name,
            'phone_number': phone_number,
            'timestamp': datetime.now().isoformat()
        }
        
        return await self.trigger_workflow('court-reminder', payload)
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of all workflows"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {}
            if self.n8n_api_key:
                headers['X-N8N-API-KEY'] = self.n8n_api_key
            
            async with self.session.get(
                f"{self.n8n_base_url}/api/v1/workflows",
                headers=headers
            ) as response:
                if response.status == 200:
                    workflows = await response.json()
                    return {
                        'success': True,
                        'total_workflows': len(workflows.get('data', [])),
                        'active_workflows': len([w for w in workflows.get('data', []) if w.get('active')]),
                        'workflows': workflows.get('data', [])
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_triggers(self) -> Dict[str, N8NWorkflowTrigger]:
        """Get available workflow triggers"""
        return {
            'court_update': N8NWorkflowTrigger(
                webhook_url=f"{self.n8n_webhook_base}/court-update",
                workflow_name="Court Update Notification",
                trigger_type="webhook",
                payload_schema={
                    'case_number': 'string',
                    'message': 'string', 
                    'phone_number': 'string',
                    'timestamp': 'string'
                }
            ),
            'document_backup': N8NWorkflowTrigger(
                webhook_url=f"{self.n8n_webhook_base}/process-document",
                workflow_name="Document Backup",
                trigger_type="webhook",
                payload_schema={
                    'case_number': 'string',
                    'document_type': 'string',
                    'file_content': 'string',
                    'folder_id': 'string'
                }
            ),
            'calendar_event': N8NWorkflowTrigger(
                webhook_url=f"{self.n8n_webhook_base}/calendar-event",
                workflow_name="Calendar Event Creation",
                trigger_type="webhook",
                payload_schema={
                    'case_number': 'string',
                    'parties': 'string',
                    'hearing_datetime': 'string',
                    'court_name': 'string'
                }
            ),
            'hearing_reminder': N8NWorkflowTrigger(
                webhook_url=f"{self.n8n_webhook_base}/court-reminder",
                workflow_name="Hearing Reminder",
                trigger_type="webhook",
                payload_schema={
                    'case_number': 'string',
                    'hearing_date': 'string',
                    'hearing_time': 'string',
                    'court_name': 'string',
                    'phone_number': 'string'
                }
            )
        }