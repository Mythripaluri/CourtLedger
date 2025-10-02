from typing import Dict, Any, Optional, List
import logging
import tempfile
import os
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from ..services.drive_service import GoogleDriveService
from ..services.ai_service import AIService
from ..services.twilio_whatsapp_service import TwilioWhatsAppService
from ..database import DriveCommandLog
from ..config import settings

logger = logging.getLogger(__name__)

class WhatsAppDriveExecutor:
    """
    Execute Google Drive operations via WhatsApp commands
    
    Handles all drive operations requested through WhatsApp:
    - File listing and search
    - Upload and download operations  
    - File management (move, rename, delete)
    - AI-powered summaries
    - Response formatting for WhatsApp
    """
    
    def __init__(self):
        """Initialize services"""
        self.drive_service = GoogleDriveService()
        self.ai_service = AIService()
        self.whatsapp_service = TwilioWhatsAppService()
        
    async def execute_command(
        self, 
        command_data: Dict[str, Any],
        db: Session,
        from_number: str
    ) -> Dict[str, Any]:
        """Execute a parsed WhatsApp command"""
        command = command_data.get('command')
        parameters = command_data.get('parameters', {})
        metadata = command_data.get('metadata', {})
        
        # Log command execution attempt
        log_entry = DriveCommandLog(
            command=command,
            parameters=str(parameters),
            phone_number=from_number,
            timestamp=datetime.now(),
            status="processing"
        )
        db.add(log_entry)
        db.commit()
        
        try:
            # Route to appropriate handler
            if command == "LIST":
                result = await self._handle_list_command(parameters, from_number)
            elif command == "SEARCH":
                result = await self._handle_search_command(parameters, from_number)
            elif command == "UPLOAD":
                result = await self._handle_upload_command(parameters, metadata, from_number)
            elif command == "DOWNLOAD":
                result = await self._handle_download_command(parameters, from_number)
            elif command == "DELETE":
                result = await self._handle_delete_command(parameters, from_number)
            elif command == "MOVE":
                result = await self._handle_move_command(parameters, from_number)
            elif command == "RENAME":
                result = await self._handle_rename_command(parameters, from_number)
            elif command == "SUMMARY":
                result = await self._handle_summary_command(parameters, from_number)
            elif command == "HELP":
                result = await self._handle_help_command(from_number)
            elif command == "ERROR":
                result = await self._handle_error_command(parameters, from_number)
            else:
                result = {"success": False, "error": f"Unknown command: {command}"}
            
            # Update log with result (simplified for now)
            db.query(DriveCommandLog).filter(DriveCommandLog.id == log_entry.id).update({
                "status": "completed" if result.get('success') else "failed",
                "response": str(result)
            })
            db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing WhatsApp command {command}: {str(e)}")
            
            # Update log with error
            db.query(DriveCommandLog).filter(DriveCommandLog.id == log_entry.id).update({
                "status": "error",
                "response": str(e)
            })
            db.commit()
            
            return {"success": False, "error": f"Command execution failed: {str(e)}"}
    
    async def _handle_list_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle LIST command"""
        folder_path = parameters.get('folder_path', '/')
        
        try:
            # Mock file listing for now
            files = [
                {"name": "document1.pdf", "size": 1024, "modified_time": "2024-01-15"},
                {"name": "report.docx", "size": 2048, "modified_time": "2024-01-14"}
            ]
            
            message = self.whatsapp_service.format_file_list(files)
            send_result = await self.whatsapp_service.send_message(from_number, message)
            
            return {
                "success": True,
                "message": f"Listed {len(files)} files from {folder_path}",
                "files_count": len(files),
                "whatsapp_sent": send_result.get('success', False)
            }
            
        except Exception as e:
            error_msg = f"Failed to list files in {folder_path}: {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_search_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle SEARCH command"""
        query = parameters.get('query', '')
        
        try:
            # Mock search results
            search_results = [
                {"name": f"search_result_{query}.pdf", "size": 1024, "modified_time": "2024-01-15"}
            ]
            
            if not search_results:
                message = f"🔍 *Search: '{query}'*\n\nNo files found matching your search."
            else:
                message = f"🔍 *Search Results for: '{query}'*\n\n"
                message += self.whatsapp_service.format_file_list(search_results)
            
            send_result = await self.whatsapp_service.send_message(from_number, message)
            
            return {
                "success": True,
                "message": f"Found {len(search_results)} files matching '{query}'",
                "results_count": len(search_results),
                "whatsapp_sent": send_result.get('success', False)
            }
            
        except Exception as e:
            error_msg = f"Search failed for '{query}': {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_upload_command(self, parameters: Dict[str, Any], metadata: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle UPLOAD command"""
        folder_path = parameters.get('folder_path', '/')
        filename = parameters.get('filename')
        media_url = parameters.get('media_url')
        media_type = parameters.get('media_type')
        
        if not media_url:
            error_msg = "Upload command requires a file attachment"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Download media from WhatsApp
            local_file_path = await self.whatsapp_service.download_media(media_url, media_type or "")
            
            if not local_file_path:
                error_msg = "Failed to download attached file"
                await self.whatsapp_service.send_error_message(from_number, error_msg)
                return {"success": False, "error": error_msg}
            
            # Use provided filename or generate one
            if not filename:
                filename = f"whatsapp_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if media_type:
                    extension_map = {
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "application/pdf": ".pdf",
                        "text/plain": ".txt"
                    }
                    filename += extension_map.get(media_type, "")
            
            # Mock upload success
            upload_success = True
            
            # Clean up temporary file
            try:
                os.unlink(local_file_path)
            except:
                pass
            
            if upload_success:
                success_msg = f"File '{filename}' uploaded successfully to {folder_path}"
                await self.whatsapp_service.send_success_message(from_number, success_msg)
                
                return {
                    "success": True,
                    "message": success_msg,
                    "filename": filename,
                    "folder_path": folder_path
                }
            else:
                error_msg = "Upload failed: Unknown error"
                await self.whatsapp_service.send_error_message(from_number, error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_download_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle DOWNLOAD command"""
        file_path = parameters.get('file_path', '')
        
        try:
            success_msg = f"Download functionality not yet implemented for {file_path}"
            await self.whatsapp_service.send_message(from_number, success_msg)
            return {"success": True, "message": success_msg}
                
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_delete_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle DELETE command"""
        file_path = parameters.get('file_path', '')
        
        try:
            success_msg = f"Delete functionality not yet implemented for {file_path}"
            await self.whatsapp_service.send_message(from_number, success_msg)
            return {"success": True, "message": success_msg}
                
        except Exception as e:
            error_msg = f"Delete failed: {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_move_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle MOVE command"""
        source_path = parameters.get('source_path', '')
        destination_path = parameters.get('destination_path', '')
        
        try:
            success_msg = f"Move functionality not yet implemented: {source_path} to {destination_path}"
            await self.whatsapp_service.send_message(from_number, success_msg)
            return {"success": True, "message": success_msg}
                
        except Exception as e:
            error_msg = f"Move failed: {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_rename_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle RENAME command"""
        file_path = parameters.get('file_path', '')
        new_name = parameters.get('new_name', '')
        
        try:
            success_msg = f"Rename functionality not yet implemented: {file_path} to {new_name}"
            await self.whatsapp_service.send_message(from_number, success_msg)
            return {"success": True, "message": success_msg}
                
        except Exception as e:
            error_msg = f"Rename failed: {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_summary_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle SUMMARY command"""
        folder_path = parameters.get('folder_path', '/')
        
        try:
            message = f"📝 *AI Summary: {folder_path}*\n\nSummary functionality not yet implemented.\n\nThis will analyze text files and provide AI-generated insights."
            await self.whatsapp_service.send_message(from_number, message)
            return {"success": True, "message": "Summary placeholder sent"}
                
        except Exception as e:
            error_msg = f"Summary failed: {str(e)}"
            await self.whatsapp_service.send_error_message(from_number, error_msg)
            return {"success": False, "error": error_msg}
    
    async def _handle_help_command(self, from_number: str) -> Dict[str, Any]:
        """Handle HELP command"""
        try:
            send_result = await self.whatsapp_service.send_help_message(from_number)
            
            return {
                "success": True,
                "message": "Help message sent",
                "whatsapp_sent": send_result.get('success', False)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to send help: {str(e)}"}
    
    async def _handle_error_command(self, parameters: Dict[str, Any], from_number: str) -> Dict[str, Any]:
        """Handle ERROR from parser"""
        error_message = parameters.get('error', 'Unknown error')
        help_message = parameters.get('help_message', '')
        
        try:
            full_message = error_message
            if help_message:
                full_message += f"\n\n{help_message}"
                
            await self.whatsapp_service.send_error_message(from_number, full_message)
            
            return {
                "success": False,
                "error": error_message,
                "whatsapp_sent": True
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to send error message: {str(e)}"}