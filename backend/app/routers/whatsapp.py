from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import time
import logging

from ..database import get_db, DriveCommandLog
from ..schemas import WhatsAppMessage, WhatsAppResponse, DriveCommandResponse
from ..services.whatsapp_parser import WhatsAppCommandParser
from ..services.twilio_whatsapp_service import TwilioWhatsAppService
from ..services.whatsapp_drive_executor import WhatsAppDriveExecutor
from ..services.drive_service import GoogleDriveService
from ..services.ai_service import AIService
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_twilio_signature: Optional[str] = Header(None)
):
    """
    Enhanced webhook endpoint for WhatsApp messages via Twilio
    
    Handles:
    - Message parsing and validation
    - Media file processing
    - Command execution
    - Response formatting
    - Webhook signature verification
    """
    whatsapp_service = TwilioWhatsAppService()
    parser = WhatsAppCommandParser()
    executor = WhatsAppDriveExecutor()
    
    try:
        # Parse incoming webhook data
        form_data = await request.form()
        
        # Convert form data to strings
        form_dict = {}
        for key, value in form_data.items():
            if isinstance(value, str):
                form_dict[key] = value
            else:
                form_dict[key] = str(value)
        
        # Extract message components
        from_number = form_dict.get("From", "").replace("whatsapp:", "")
        message_body = form_dict.get("Body", "")
        media_url = form_dict.get("MediaUrl0")
        media_type = form_dict.get("MediaContentType0")
        message_sid = form_dict.get("MessageSid")
        
        # Validate webhook signature if enabled
        if settings.twilio_auth_token and x_twilio_signature:
            webhook_url = str(request.url)
            is_valid = whatsapp_service.validate_webhook(
                webhook_url, form_dict, x_twilio_signature
            )
            if not is_valid:
                logger.warning(f"Invalid webhook signature from {from_number}")
                raise HTTPException(status_code=403, detail="Invalid webhook signature")
        
        # Validate required fields
        if not from_number:
            raise HTTPException(status_code=400, detail="Missing sender information")
        
        if not message_body and not media_url:
            raise HTTPException(status_code=400, detail="Empty message received")
        
        logger.info(f"Received WhatsApp message from {from_number}: {message_body[:50]}...")
        
        # Parse command with media support
        command_data = parser.parse_message(
            message=message_body,
            media_url=media_url,
            media_type=media_type,
            from_number=from_number
        )
        
        if not command_data:
            # Send error response for unrecognized commands
            await whatsapp_service.send_error_message(
                from_number, 
                "I didn't understand that command. Type *HELP* for available commands."
            )
            return {"status": "error", "message": "Invalid command"}
        
        # Execute the command
        execution_result = await executor.execute_command(
            command_data=command_data,
            db=db,
            from_number=from_number
        )
        
        # Return success response
        return {
            "status": "success" if execution_result.get('success') else "error",
            "message": execution_result.get('message', 'Command processed'),
            "command": command_data.get('command'),
            "message_sid": message_sid
        }
        
        # Log the command
        start_time = time.time()
        command_log = DriveCommandLog(
            user_phone=from_number,
            command=command_data["command"],
            parameters=json.dumps(command_data["parameters"]),
            status="pending"
        )
        db.add(command_log)
        db.commit()
        db.refresh(command_log)
        
        # Execute the command
        drive_service = GoogleDriveService()
        response = await execute_drive_command(
            command_data, drive_service, whatsapp_message, db
        )
        
        # Update command log
        execution_time = time.time() - start_time
        command_log.status = response.status
        command_log.response_message = response.message
        command_log.execution_time = execution_time
        
        if response.status == "error":
            command_log.error_details = response.message
        
        db.commit()
        
        return WhatsAppResponse(
            status=response.status,
            message=response.message,
            data=response.data
        )
        
    except Exception as e:
        return WhatsAppResponse(
            status="error",
            message=f"Failed to process WhatsApp message: {str(e)}"
        )

async def execute_drive_command(
    command_data: Dict[str, Any],
    drive_service: GoogleDriveService,
    whatsapp_message: WhatsAppMessage,
    db: Session
) -> DriveCommandResponse:
    """
    Execute the parsed WhatsApp command
    """
    command = command_data["command"]
    params = command_data["parameters"]
    
    try:
        if command == "LIST":
            folder_path = params.get("folder_path", "/")
            files = await drive_service.list_files(folder_path)
            
            # Format response for WhatsApp
            if not files:
                message = f"No files found in folder: {folder_path}"
            else:
                message = f"Files in {folder_path}:\n"
                for i, file in enumerate(files[:10], 1):  # Limit to 10 files
                    message += f"{i}. {file['name']} ({file['type']})\n"
                if len(files) > 10:
                    message += f"... and {len(files) - 10} more files"
            
            return DriveCommandResponse(
                status="success",
                message=message,
                data={"files": files}
            )
        
        elif command == "DELETE":
            file_path = params.get("file_path")
            if not file_path:
                return DriveCommandResponse(
                    status="error",
                    message="File path is required for DELETE command"
                )
            
            result = await drive_service.delete_file(file_path)
            if result:
                message = f"Successfully deleted: {file_path}"
            else:
                message = f"Failed to delete: {file_path}"
            
            return DriveCommandResponse(
                status="success" if result else "error",
                message=message
            )
        
        elif command == "MOVE":
            source_path = params.get("source_path")
            dest_path = params.get("dest_path")
            
            if not source_path or not dest_path:
                return DriveCommandResponse(
                    status="error",
                    message="Both source and destination paths are required for MOVE command"
                )
            
            result = await drive_service.move_file(source_path, dest_path)
            if result:
                message = f"Successfully moved {source_path} to {dest_path}"
            else:
                message = f"Failed to move {source_path} to {dest_path}"
            
            return DriveCommandResponse(
                status="success" if result else "error",
                message=message
            )
        
        elif command == "RENAME":
            file_path = params.get("file_path")
            new_name = params.get("new_name")
            
            if not file_path or not new_name:
                return DriveCommandResponse(
                    status="error",
                    message="Both file path and new name are required for RENAME command"
                )
            
            result = await drive_service.rename_file(file_path, new_name)
            if result:
                message = f"Successfully renamed {file_path} to {new_name}"
            else:
                message = f"Failed to rename {file_path}"
            
            return DriveCommandResponse(
                status="success" if result else "error",
                message=message
            )
        
        elif command == "SUMMARY":
            folder_path = params.get("folder_path", "/")
            files = await drive_service.list_files(folder_path)
            
            # Filter text-based files for summarization
            text_files = [f for f in files if f['type'] in ['pdf', 'doc', 'docx', 'txt']]
            
            if not text_files:
                return DriveCommandResponse(
                    status="success",
                    message=f"No text files found in {folder_path} for summarization"
                )
            
            ai_service = AIService()
            summaries = []
            
            for file in text_files[:5]:  # Limit to 5 files for cost control
                content = await drive_service.download_file_content(file['id'])
                if content:
                    summary = await ai_service.summarize_text(content, file['name'])
                    summaries.append(f"📄 {file['name']}: {summary}")
            
            if summaries:
                message = f"Summary of files in {folder_path}:\n\n" + "\n\n".join(summaries)
            else:
                message = f"Could not generate summaries for files in {folder_path}"
            
            return DriveCommandResponse(
                status="success",
                message=message,
                data={"summaries": summaries}
            )
        
        elif command == "UPLOAD":
            if not whatsapp_message.media_url:
                return DriveCommandResponse(
                    status="error",
                    message="No file attached. Please attach a file to upload."
                )
            
            folder_path = params.get("folder_path", "/")
            filename = params.get("filename") or "whatsapp_upload"
            
            # Download file from WhatsApp media URL
            file_content = await drive_service.download_media(whatsapp_message.media_url)
            if not file_content:
                return DriveCommandResponse(
                    status="error",
                    message="Failed to download attached file"
                )
            
            # Upload to Google Drive
            result = await drive_service.upload_file(
                folder_path, filename, file_content, whatsapp_message.media_type
            )
            
            if result:
                message = f"Successfully uploaded {filename} to {folder_path}"
            else:
                message = f"Failed to upload {filename}"
            
            return DriveCommandResponse(
                status="success" if result else "error",
                message=message
            )
        
        elif command == "HELP":
            help_message = """Available commands:
            
📁 LIST /FolderName - List files in folder
🗑️ DELETE /path/file.pdf - Delete a file
📦 MOVE /source/file.pdf /dest/ - Move file
✏️ RENAME /path/file.pdf NewName.pdf - Rename file
📝 SUMMARY /FolderName - AI summary of text files
⬆️ UPLOAD /FolderName filename.ext - Upload attached file

Example: LIST /Documents"""
            
            return DriveCommandResponse(
                status="success",
                message=help_message
            )
        
        else:
            return DriveCommandResponse(
                status="error",
                message=f"Unknown command: {command}. Type 'HELP' for available commands."
            )
    
    except Exception as e:
        return DriveCommandResponse(
            status="error",
            message=f"Error executing {command}: {str(e)}"
        )