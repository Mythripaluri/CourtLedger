#!/bin/bash

# Court Case Tracker & WhatsApp Drive Assistant
# Installation and Setup Script

echo "🏛️ Setting up Court Case Tracker & WhatsApp Drive Assistant Backend..."

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1)
if [[ $python_version == *"Python 3."* ]]; then
    echo "✅ Python detected: $python_version"
else
    echo "❌ Python 3.x is required. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "Creating required directories..."
mkdir -p static/pdfs
mkdir -p static/uploads
mkdir -p logs

# Copy environment file
echo "Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env file with your API keys and credentials"
else
    echo "✅ .env file already exists"
fi

# Create database
echo "Setting up database..."
python -c "
from app.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Check Chrome/Chromium installation
echo "Checking for Chrome/Chromium..."
if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null || command -v chrome &> /dev/null; then
    echo "✅ Chrome/Chromium detected"
else
    echo "⚠️  Chrome/Chromium not detected. Please install for web scraping functionality."
    echo "   Ubuntu: sudo apt-get install chromium-browser"
    echo "   MacOS: brew install --cask google-chrome"
    echo "   Windows: Download from https://www.google.com/chrome/"
fi

# Check ChromeDriver
echo "Checking ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver detected"
else
    echo "⚠️  ChromeDriver not detected. Installing via webdriver-manager..."
    pip install webdriver-manager
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials:"
echo "   - Google Client ID & Secret (for Drive/Calendar)"
echo "   - OpenAI or Anthropic API Key (for AI summaries)"
echo "   - Twilio credentials (for WhatsApp integration)"
echo ""
echo "2. Start the development server:"
echo "   python main.py"
echo ""
echo "3. Or start with auto-reload:"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Access the API documentation at:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔧 Configuration tips:"
echo "   - Set up Google OAuth2 credentials at: https://console.cloud.google.com/"
echo "   - Enable Google Drive API and Google Calendar API"
echo "   - Add redirect URI: http://localhost:8000/api/integrations/google/callback"
echo "   - For WhatsApp integration, set up Twilio webhook: http://your-domain:8000/api/whatsapp/webhook"
echo ""
echo "📚 For detailed setup instructions, see README.md"