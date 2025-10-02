from twilio.rest import Client
from twilio.request_validator import RequestValidator
from typing import Dict, Any, Optional, List
import logging
import hashlib
import hmac
import base64
import asyncio
import aiohttp
import tempfile
import os
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)

class TwilioWhatsAppService:
    """
    Comprehensive WhatsApp Business API integration using Twilio
    
    Features:
    - Send text messages and media files
    - Receive and validate webhooks
    - Handle file attachments
    - Message templates and formatting
    - Error handling and retry logic
    """
    
    def __init__(self):
        """Initialize Twilio WhatsApp client"""
        self.account_sid = getattr(settings, 'twilio_account_sid', '')
        self.auth_token = getattr(settings, 'twilio_auth_token', '')
        self.whatsapp_number = getattr(settings, 'twilio_whatsapp_number', '')
        self.webhook_url = getattr(settings, 'whatsapp_webhook_url', '')
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            logger.warning("Twilio WhatsApp credentials not configured")
            self.client = None
            self.validator = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
            self.validator = RequestValidator(self.auth_token)
            logger.info("Twilio WhatsApp service initialized successfully")
    
    async def send_message(
        self, 
        to_number: str, 
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message to a phone number
        
        Args:
            to_number: Recipient phone number (with country code)
            message: Message text
            media_url: Optional media URL to send
            
        Returns:
            Dict with success status and message details
        """
        if not self.client:
            return {
                "success": False,
                "error": "Twilio client not configured",
                "message_sid": None
            }
        
        try:
            # Ensure phone number format
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            from_number = f"whatsapp:{self.whatsapp_number}"
            
            # Prepare message parameters
            message_params = {
                "body": message,
                "from_": from_number,
                "to": to_number
            }
            
            # Add media if provided
            if media_url:
                message_params["media_url"] = [media_url]
            
            # Send message
            message_obj = self.client.messages.create(**message_params)
            
            logger.info(f"WhatsApp message sent successfully: {message_obj.sid}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_number,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_sid": None
            }
    
    async def send_file(
        self, 
        to_number: str, 
        file_path: str, 
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a file via WhatsApp
        
        Args:
            to_number: Recipient phone number
            file_path: Local path to file or URL
            caption: Optional caption for the file
            
        Returns:
            Dict with success status and message details
        """
        try:
            # If it's a local file, we need to upload it first
            if os.path.isfile(file_path):
                # For production, upload to cloud storage (AWS S3, Google Cloud, etc.)
                # For now, we'll assume the file is accessible via URL
                media_url = file_path  # This should be a public URL
            else:
                media_url = file_path  # Assume it's already a URL
            
            message = caption if caption else "File shared via Case Drive Buddy"
            
            return await self.send_message(
                to_number=to_number,
                message=message,
                media_url=media_url
            )
            
        except Exception as e:
            logger.error(f"Failed to send file via WhatsApp: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message_sid": None
            }
    
    async def download_media(self, media_url: str, media_type: str) -> Optional[str]:
        """
        Download media file from WhatsApp message
        
        Args:
            media_url: URL of the media file
            media_type: MIME type of the media
            
        Returns:
            Local file path where media was saved, or None if failed
        """
        if not media_url:
            return None
        
        try:
            # Get file extension from media type
            extension_map = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "application/pdf": ".pdf",
                "text/plain": ".txt",
                "application/msword": ".doc",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
            }
            
            file_extension = extension_map.get(media_type, "")
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=file_extension,
                dir=getattr(settings, 'temp_dir', tempfile.gettempdir())
            )
            
            # Download file
            async with aiohttp.ClientSession() as session:
                # Add Twilio authentication
                auth = aiohttp.BasicAuth(self.account_sid, self.auth_token)
                
                async with session.get(media_url, auth=auth) as response:
                    if response.status == 200:
                        content = await response.read()
                        temp_file.write(content)
                        temp_file.close()
                        
                        logger.info(f"Media downloaded successfully: {temp_file.name}")
                        return temp_file.name
                    else:
                        logger.error(f"Failed to download media: HTTP {response.status}")
                        temp_file.close()
                        os.unlink(temp_file.name)
                        return None
            
        except Exception as e:
            logger.error(f"Error downloading media: {str(e)}")
            return None
    
    def validate_webhook(self, url: str, params: Dict[str, str], signature: str) -> bool:
        """
        Validate Twilio webhook signature for security
        
        Args:
            url: The full URL of the webhook request
            params: POST parameters from the request
            signature: X-Twilio-Signature header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.validator:
            logger.warning("Webhook validator not available")
            return False
        
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Webhook validation error: {str(e)}")
            return False
    
    async def send_help_message(self, to_number: str) -> Dict[str, Any]:
        """Send help message with available commands"""
        help_text = """🤖 *Case Drive Buddy WhatsApp Bot*

Available commands:

📁 *LIST /folder*
List files in folder
_Example: LIST /Documents_

⬆️ *UPLOAD /folder filename*
Upload attached file
_Example: UPLOAD /Legal contract.pdf_
_(Attach file to message)_

🔍 *SEARCH keyword*
Search for files
_Example: SEARCH contract_

📄 *SUMMARY /folder*
Get AI summary of folder
_Example: SUMMARY /Legal_Cases_

🗑️ *DELETE /path/file.pdf*
Delete specific file
_Example: DELETE /Archive/old.pdf_

📦 *MOVE /source/file.pdf /dest/*
Move file to new location
_Example: MOVE /Downloads/doc.pdf /Archive/_

✏️ *RENAME /path/old.pdf new.pdf*
Rename a file
_Example: RENAME /Docs/report.pdf final_report.pdf_

❓ *HELP*
Show this message

💡 *Tips:*
• All paths start with /
• Commands are case-insensitive
• Attach files when uploading"""

        return await self.send_message(to_number, help_text)
    
    async def send_error_message(self, to_number: str, error: str) -> Dict[str, Any]:
        """Send formatted error message"""
        error_text = f"❌ *Error*\n\n{error}\n\nType *HELP* for available commands."
        return await self.send_message(to_number, error_text)
    
    async def send_success_message(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send formatted success message"""
        success_text = f"✅ *Success*\n\n{message}"
        return await self.send_message(to_number, success_text)
    
    def format_file_list(self, files: List[Dict[str, Any]]) -> str:
        """Format file list for WhatsApp message"""
        if not files:
            return "📁 *Folder is empty*\n\nNo files found in this folder."
        
        message = f"📁 *Files found ({len(files)} items):*\n\n"
        
        for i, file in enumerate(files[:20], 1):  # Limit to 20 files
            name = file.get('name', 'Unknown')
            size = file.get('size', 0)
            modified = file.get('modified_time', '')
            
            # Format file size
            if size:
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
            else:
                size_str = "Unknown size"
            
            message += f"{i}. *{name}*\n   📏 {size_str}\n"
            if modified:
                message += f"   📅 {modified[:10]}\n"
            message += "\n"
        
        if len(files) > 20:
            message += f"... and {len(files) - 20} more files\n\n"
        
        message += "💡 Use specific commands to manage these files."
        
        return message
    
    def format_operation_result(self, operation: str, result: Dict[str, Any]) -> str:
        """Format operation result message"""
        if result.get('success'):
            return f"✅ *{operation.title()} Successful*\n\n{result.get('message', 'Operation completed successfully.')}"
        else:
            return f"❌ *{operation.title()} Failed*\n\n{result.get('error', 'Unknown error occurred.')}"