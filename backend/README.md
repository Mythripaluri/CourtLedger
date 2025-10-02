# Court Case Tracker & WhatsApp Drive Assistant Backend

A comprehensive FastAPI backend for managing court cases and WhatsApp-based Google Drive operations.

## Features

### Court Case Tracker
- **Case Search**: Scrape case details from High Court and District Court websites
- **Cause List Management**: Daily cause list scraping and PDF generation
- **Document Downloads**: Judgment and cause list PDF downloads
- **Recent Searches**: Track and revisit previous case searches

### WhatsApp Drive Assistant
- **WhatsApp Commands**: Process natural language commands via WhatsApp
- **Google Drive Integration**: List, delete, move, rename, upload files
- **AI Summaries**: Generate intelligent summaries of documents
- **Command History**: Track all user commands and responses

### Integrations
- **Google Calendar**: Automatic hearing date reminders
- **n8n Workflows**: Automated notifications and document backup
- **AI Services**: OpenAI/Anthropic integration for document processing

## Installation

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser (for web scraping)
- Google API credentials
- OpenAI/Anthropic API keys (optional)
- Twilio account for WhatsApp (optional)

### Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

3. **Database setup**:
   ```bash
   # Database will be created automatically on first run
   python main.py
   ```

4. **Chrome WebDriver setup**:
   ```bash
   # Install ChromeDriver for your system
   # https://chromedriver.chromium.org/
   ```

## Configuration

### Required Environment Variables

```env
# Google APIs
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# AI Services (at least one required for summaries)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# WhatsApp (optional, for WhatsApp integration)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API and Google Calendar API
4. Create OAuth2 credentials
5. Add redirect URI: `http://localhost:8000/api/integrations/google/callback`

### Twilio WhatsApp Setup

1. Create [Twilio account](https://www.twilio.com/)
2. Set up WhatsApp Sandbox or get approved sender
3. Configure webhook URL: `http://your-domain:8000/api/whatsapp/webhook`

## API Endpoints

### Court Case Tracker

```
POST /api/court/fetch-case
POST /api/court/fetch-causelist
GET  /api/court/download-judgment
GET  /api/court/download-causelist
GET  /api/court/recent-searches
```

### WhatsApp Drive Assistant

```
POST /api/whatsapp/webhook
```

### Google Drive

```
GET    /api/drive/list
DELETE /api/drive/delete
POST   /api/drive/move
POST   /api/drive/rename
POST   /api/drive/upload
POST   /api/drive/summary
GET    /api/drive/search
```

### Integrations

```
GET  /api/integrations/status
GET  /api/integrations/google/auth
GET  /api/integrations/google/callback
POST /api/integrations/google-calendar/create-event
GET  /api/integrations/google-calendar/events
POST /api/integrations/n8n/webhook
```

## WhatsApp Commands

The system supports natural language commands via WhatsApp:

- `LIST /Documents` - List files in Documents folder
- `DELETE /path/file.pdf` - Delete a specific file
- `MOVE /source/file.pdf /destination/` - Move file
- `RENAME /path/old.pdf new_name.pdf` - Rename file
- `SUMMARY /FolderName` - Get AI summary of text files
- `UPLOAD /FolderName filename.ext` - Upload attached file
- `HELP` - Show available commands

## n8n Workflows

Pre-configured workflows for automation:

### Court Hearing Reminders
- Triggers: Manual webhook call
- Action: Send WhatsApp reminder with case details
- Webhook: `/api/integrations/n8n/webhook`

### Document Backup
- Triggers: Document upload/creation
- Action: Backup to Google Drive
- Features: Automatic organization by case number

### Daily Cause List Notifications
- Triggers: Daily at 6 AM
- Action: Fetch and send cause list updates
- Features: WhatsApp notifications for subscribed users

## Running the Application

### Development
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UnicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Court Website Integration

### High Court Portal
- URL: https://hcservices.ecourts.gov.in/hcservices/main.php
- Method: Selenium-based scraping
- Features: Case search, cause list extraction

### District Court Portal  
- URL: https://services.ecourts.gov.in/ecourtindia_v6/
- Method: Selenium-based scraping
- Features: Case search, cause list extraction

**Note**: Web scraping implementation includes:
- Retry mechanisms for reliability
- Error handling for court portal changes
- Caching to reduce server load
- Respectful request intervals

## Database Schema

### Tables
- `case_queries` - Store case search results
- `cause_lists` - Daily cause list data
- `drive_command_logs` - WhatsApp command history
- `file_summaries` - AI-generated file summaries

### Relationships
- Cases linked to cause list entries
- Commands linked to file operations
- Summaries cached for quick retrieval

## Error Handling

The API includes comprehensive error handling:

- **Court Portal Errors**: Graceful fallbacks for site changes
- **WhatsApp Errors**: User-friendly error messages
- **Google API Errors**: OAuth token refresh handling
- **AI Service Errors**: Fallback to basic summaries

## Rate Limiting

Built-in protection against abuse:
- Max 60 requests per minute per IP
- WhatsApp command throttling
- Court portal request limiting

## Security

Security measures implemented:
- Environment variable protection
- OAuth2 secure token handling
- Input validation and sanitization
- CORS configuration for frontend integration

## Monitoring

Logging and monitoring features:
- Structured logging for all operations
- Error tracking and alerting
- Performance metrics collection
- User activity monitoring

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For issues and support:
1. Check the documentation
2. Search existing issues
3. Create new issue with detailed description
4. Include error logs and environment details