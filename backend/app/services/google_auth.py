from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import secrets
import json

from ..config import settings

class GoogleAuthService:
    """Handle Google OAuth2 authentication"""
    
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri]
            }
        }
        
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/calendar'
        ]
    
    def get_authorization_url(self):
        """Generate Google OAuth2 authorization URL"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                redirect_uri=settings.google_redirect_uri
            )
            
            # Generate state for security
            state = secrets.token_urlsafe(32)
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )
            
            return auth_url, state
            
        except Exception as e:
            print(f"Error generating auth URL: {str(e)}")
            return None, None
    
    async def exchange_code_for_token(self, code: str, state: str):
        """Exchange authorization code for access token"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes,
                redirect_uri=settings.google_redirect_uri
            )
            
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # TODO: Store credentials securely in database
            # You would typically store:
            # - credentials.token (access token)
            # - credentials.refresh_token
            # - credentials.token_uri
            # - credentials.client_id
            # - credentials.client_secret
            
            return credentials
            
        except Exception as e:
            print(f"Error exchanging code for token: {str(e)}")
            return None