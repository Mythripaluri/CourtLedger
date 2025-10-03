from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # Database
        # Use absolute path for database to avoid path issues
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "court_tracker.db")
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
        
        # Google APIs
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/integrations/google/callback")
        
        # AI Services
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ai_enabled = os.getenv("AI_ENABLED", "true").lower() == "true"
        self.default_ai_model = os.getenv("DEFAULT_AI_MODEL", "gpt-4")
        self.ai_max_tokens = int(os.getenv("AI_MAX_TOKENS", "2000"))
        self.ai_temperature = float(os.getenv("AI_TEMPERATURE", "0.2"))
        self.ai_timeout = int(os.getenv("AI_TIMEOUT", "30"))  # seconds
        
        # Twilio WhatsApp
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.whatsapp_webhook_url = os.getenv("WHATSAPP_WEBHOOK_URL", "http://localhost:8000/api/whatsapp/webhook")
        
        # WhatsApp Settings
        self.whatsapp_enabled = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
        self.whatsapp_max_file_size = int(os.getenv("WHATSAPP_MAX_FILE_SIZE", "16777216"))  # 16MB
        self.temp_dir = os.getenv("TEMP_DIR", "./temp")
        
        # n8n
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        self.n8n_api_key = os.getenv("N8N_API_KEY")
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.n8n_base_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
        self.n8n_webhook_base = os.getenv("N8N_WEBHOOK_BASE", f"{self.n8n_base_url}/webhook")
        
        # Court URLs
        self.high_court_url = "https://hcservices.ecourts.gov.in/hcservices/main.php"
        self.district_court_url = "https://services.ecourts.gov.in/ecourtindia_v6/"
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # File storage
        self.upload_dir = "static/uploads"
        self.pdf_dir = "static/pdfs"
        
        # Document Processing
        self.supported_file_types = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
        self.ocr_enabled = os.getenv("OCR_ENABLED", "true").lower() == "true"
        self.text_extraction_timeout = int(os.getenv("TEXT_EXTRACTION_TIMEOUT", "60"))  # seconds
        
        # Rate limiting
        self.max_requests_per_minute = 60

settings = Settings()