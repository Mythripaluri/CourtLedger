import re
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppCommandParser:
    """Enhanced WhatsApp command parser for Google Drive operations"""
    
    def __init__(self):
        self.commands = {
            "LIST": self._parse_list_command,
            "DELETE": self._parse_delete_command,
            "MOVE": self._parse_move_command,
            "RENAME": self._parse_rename_command,
            "SUMMARY": self._parse_summary_command,
            "UPLOAD": self._parse_upload_command,
            "SEARCH": self._parse_search_command,
            "DOWNLOAD": self._parse_download_command,
            "HELP": self._parse_help_command,
        }
        
        # Supported file types for upload
        self.supported_file_types = {
            'application/pdf',
            'image/jpeg',
            'image/png', 
            'text/plain',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
    
    def parse_message(
        self, 
        message: str, 
        media_url: Optional[str] = None,
        media_type: Optional[str] = None,
        from_number: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Parse WhatsApp message with media support
        
        Args:
            message: Text message content
            media_url: URL of attached media (if any)
            media_type: MIME type of attached media
            from_number: Sender's phone number
            
        Returns:
            Parsed command dictionary or None if invalid
        """
        result = self.parse_command(message)
        
        if result:
            # Add metadata
            result['metadata'] = {
                'from_number': from_number,
                'timestamp': datetime.now().isoformat(),
                'has_media': bool(media_url),
                'media_type': media_type,
                'media_url': media_url
            }
            
            # Handle media for upload commands
            if result['command'] == 'UPLOAD' and media_url:
                if self._is_supported_file_type(media_type):
                    result['parameters']['media_url'] = media_url
                    result['parameters']['media_type'] = media_type
                else:
                    return {
                        'command': 'ERROR',
                        'parameters': {
                            'error': f'Unsupported file type: {media_type}',
                            'supported_types': list(self.supported_file_types)
                        }
                    }
        
        return result
    
    def parse_command(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Parse WhatsApp message and extract command and parameters
        
        Expected formats:
        - LIST /FolderName
        - DELETE /FolderName/file.pdf
        - MOVE /source/file.pdf /destination/
        - RENAME /path/file.pdf NewName.pdf
        - SUMMARY /FolderName
        - UPLOAD /FolderName filename.ext
        - SEARCH keyword or phrase
        - DOWNLOAD /path/to/file.pdf
        - HELP
        """
        if not message or not isinstance(message, str):
            return None
            
        message = message.strip()
        
        # Extract command (first word)
        parts = message.split()
        if not parts:
            return None
            
        command = parts[0].upper()
        
        if command not in self.commands:
            return self._create_error_response(f"Unknown command: {command}")
        
        try:
            return self.commands[command](message)
        except Exception as e:
            logger.error(f"Error parsing command '{command}': {str(e)}")
            return self._create_error_response(f"Invalid command format: {str(e)}")
    
    def _parse_list_command(self, message: str) -> Dict[str, Any]:
        """Parse LIST command: LIST /FolderName"""
        parts = message.split(maxsplit=1)
        
        folder_path = "/"
        if len(parts) > 1:
            folder_path = parts[1].strip()
            if not folder_path.startswith("/"):
                folder_path = "/" + folder_path
        
        return {
            "command": "LIST",
            "parameters": {
                "folder_path": folder_path
            }
        }
    
    def _parse_delete_command(self, message: str) -> Dict[str, Any]:
        """Parse DELETE command: DELETE /FolderName/file.pdf"""
        parts = message.split(maxsplit=1)
        
        if len(parts) < 2:
            raise ValueError("DELETE command requires file path")
        
        file_path = parts[1].strip()
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        
        return {
            "command": "DELETE",
            "parameters": {
                "file_path": file_path
            }
        }
    
    def _parse_move_command(self, message: str) -> Dict[str, Any]:
        """Parse MOVE command: MOVE /source/file.pdf /destination/"""
        # Use regex to handle paths with spaces
        pattern = r'MOVE\s+(/[^\s]+)\s+(/[^\s]+)'
        match = re.match(pattern, message, re.IGNORECASE)
        
        if not match:
            raise ValueError("MOVE command requires source and destination paths")
        
        source_path = match.group(1)
        dest_path = match.group(2)
        
        return {
            "command": "MOVE",
            "parameters": {
                "source_path": source_path,
                "dest_path": dest_path
            }
        }
    
    def _parse_rename_command(self, message: str) -> Dict[str, Any]:
        """Parse RENAME command: RENAME /path/file.pdf NewName.pdf"""
        parts = message.split(maxsplit=2)
        
        if len(parts) < 3:
            raise ValueError("RENAME command requires file path and new name")
        
        file_path = parts[1].strip()
        new_name = parts[2].strip()
        
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        
        return {
            "command": "RENAME",
            "parameters": {
                "file_path": file_path,
                "new_name": new_name
            }
        }
    
    def _parse_summary_command(self, message: str) -> Dict[str, Any]:
        """Parse SUMMARY command: SUMMARY /FolderName"""
        parts = message.split(maxsplit=1)
        
        folder_path = "/"
        if len(parts) > 1:
            folder_path = parts[1].strip()
            if not folder_path.startswith("/"):
                folder_path = "/" + folder_path
        
        return {
            "command": "SUMMARY",
            "parameters": {
                "folder_path": folder_path
            }
        }
    
    def _parse_upload_command(self, message: str) -> Dict[str, Any]:
        """Parse UPLOAD command: UPLOAD /FolderName filename.ext"""
        parts = message.split()
        
        folder_path = "/"
        filename = None
        
        if len(parts) > 1:
            folder_path = parts[1].strip()
            if not folder_path.startswith("/"):
                folder_path = "/" + folder_path
        
        if len(parts) > 2:
            filename = parts[2].strip()
        
        return {
            "command": "UPLOAD",
            "parameters": {
                "folder_path": folder_path,
                "filename": filename
            }
        }
    
    def _parse_help_command(self, message: str) -> Dict[str, Any]:
        """Parse HELP command: HELP"""
        return {
            "command": "HELP",
            "parameters": {}
        }
    
    def _parse_search_command(self, message: str) -> Dict[str, Any]:
        """Parse SEARCH command: SEARCH keyword or phrase"""
        parts = message.split(maxsplit=1)
        
        if len(parts) < 2:
            return self._create_error_response("Search command requires a keyword or phrase")
        
        search_query = parts[1].strip()
        
        return {
            "command": "SEARCH",
            "parameters": {
                "query": search_query
            }
        }
    
    def _parse_download_command(self, message: str) -> Dict[str, Any]:
        """Parse DOWNLOAD command: DOWNLOAD /path/to/file.pdf"""
        parts = message.split()
        
        if len(parts) < 2:
            return self._create_error_response("Download command requires a file path")
        
        file_path = parts[1].strip()
        if not file_path.startswith("/"):
            file_path = "/" + file_path
        
        return {
            "command": "DOWNLOAD",
            "parameters": {
                "file_path": file_path
            }
        }
    
    def _is_supported_file_type(self, media_type: Optional[str]) -> bool:
        """Check if media type is supported for upload"""
        if not media_type:
            return False
        return media_type in self.supported_file_types
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "command": "ERROR",
            "parameters": {
                "error": error_message,
                "help_message": "Type 'HELP' for available commands"
            }
        }
    
    @staticmethod
    def get_help_text() -> str:
        """Return help text for all available commands"""
        return """Available WhatsApp Drive Commands:

📁 LIST /FolderName
   List all files in the specified folder
   Example: LIST /Documents

� SEARCH keyword or phrase
   Search for files containing keyword
   Example: SEARCH contract agreement

⬇️ DOWNLOAD /path/to/file.pdf
   Download a specific file
   Example: DOWNLOAD /Documents/report.pdf

⬆️ UPLOAD /FolderName filename.ext
   Upload attached file to specified folder
   Example: UPLOAD /Documents contract.pdf
   (Attach file to WhatsApp message)

�🗑️ DELETE /path/to/file.pdf
   Delete a specific file
   Example: DELETE /Documents/report.pdf

📦 MOVE /source/file.pdf /destination/
   Move file from source to destination
   Example: MOVE /Downloads/file.pdf /Archive/

✏️ RENAME /path/file.pdf NewName.pdf
   Rename a file
   Example: RENAME /Documents/old.pdf new_report.pdf

📝 SUMMARY /FolderName
   Get AI-generated summary of text files in folder
   Example: SUMMARY /Legal_Documents

❓ HELP
   Show this help message

📋 Supported file types for upload:
   PDF, Images (JPG, PNG), Text files, Word docs, Excel sheets

💡 Tips:
   • All folder paths should start with '/'
   • Commands are case-insensitive
   • Attach files when using UPLOAD command
   
Example paths: /Documents, /Legal_Cases, /Archive"""