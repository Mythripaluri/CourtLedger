# CourtLedger - Court Case Tracker & Judgment Downloader

![Indian Courts](https://img.shields.io/badge/Indian-Courts-orange)
![eCourts](https://img.shields.io/badge/eCourts-Integration-green)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-blue)

## 🎯 Project Overview

**CourtLedger** is a comprehensive web application designed for Indian legal professionals, lawyers, and citizens to efficiently track court cases, download judgments, and access daily cause lists. The application integrates with eCourts portals and provides a modern, user-friendly interface for case management.

### 🔥 Key Capabilities
- **Case Search**: Enter Case Type, Case Number, and Year to fetch detailed case information
- **Judgment Downloads**: Direct PDF downloads of court orders and judgments  
- **Cause List Access**: Daily court schedules with case listings and hearing times
- **Multi-Court Support**: High Courts and District Courts across India
- **Historical Tracking**: Complete audit trail of searches and results

## ✅ Features Implemented

### 📋 **UI - Simple Input Form**
- **Case Type** dropdown with all major Indian court case types (WP, CWP, CRL, etc.)
- **Case Number** input field with validation
- **Year** selection for precise case identification
- **Court Selection** between High Courts and District Courts
- Responsive React.js frontend with modern UI components

### 🔍 **Scraper/Fetcher - Complete Implementation**
- ✅ **All High Courts** - Integrated with eCourts portal scraping
- ✅ **All District Courts** - Comprehensive district court coverage
- ✅ **Parsed Data Extraction**:
  - Parties' names
  - Filing date
  - Next hearing date
  - Case status
  - Judgment/order URLs
- ✅ **Error Handling** - Graceful handling of invalid cases and unavailable data

### 💾 **Storage - Database Integration**
- ✅ **SQLite Database** with comprehensive schema
- ✅ **Query Storage** - Every search query and raw response stored
- ✅ **Data Models**:
  - `case_queries` - Case search history and results
  - `cause_lists` - Daily cause list entries
  - Metadata tracking (timestamps, success status, error messages)

### 📊 **Display - Rich Data Presentation**
- ✅ **Parsed Details Rendering** - Structured display of case information
- ✅ **PDF Downloads** - Direct download of judgments and orders
- ✅ **Recent Searches** - Historical query tracking
- ✅ **Error Display** - User-friendly error messages

### 📅 **Cause List Functionality**
- ✅ **Daily Cause Lists** - Fetch cases listed for specific dates
- ✅ **PDF Generation** - Downloadable cause list PDFs
- ✅ **Case Highlighting** - Highlight specific cases in cause lists
- ✅ **Court-wise Filtering** - Separate cause lists for different courts

## 🚀 Setup & Installation Guide

### **Prerequisites**
- **Python 3.8+** (Python 3.11 recommended)
- **Node.js 18+** with npm
- **Git** for version control

### **📦 Installation Steps**

#### **1. Clone Repository**
```bash
git clone https://github.com/Mythripaluri/CourtLedger.git
cd CourtLedger
```

#### **2. Frontend Setup**  
```bash
npm install
```

#### **3. Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **⚡ Quick Start (Two Options)**

#### **Option A: Demo Mode with Mock Data (Recommended)**
```bash
# Terminal 1: Start Test Server with Demo Data
python test_server.py

# Terminal 2: Start Frontend
npm run dev
```

#### **Option B: Full Production Server**
```bash
# Terminal 1: Start Full Backend
cd backend
python main.py

# Terminal 2: Start Frontend  
npm run dev
```

**🌐 Access URLs:**
- **Frontend**: `http://localhost:8081` (or `http://localhost:5173`)
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

## 🧪 Demo Data & Testing

### **🎭 Mock Data Overview**
The application includes comprehensive demo data for testing without requiring real court API access:

#### **📋 Available Demo Cases**

| Case Type | Case Number | Year | Court Type | Expected Result |
|-----------|-------------|------|------------|-----------------|
| **WP** | 5678 | 2023 | High Court | "Rajesh Kumar vs State of Delhi & Others" |
| **PIL** | 1234 | 2024 | High Court | "Citizens Welfare Association vs Municipal Corporation" |
| **CWP** | 9876 | 2024 | High Court | "Tech Solutions Pvt Ltd vs Income Tax Department" |
| **CC** | 456 | 2024 | District Court | "State vs Amit Sharma" |
| **CS** | 789 | 2023 | District Court | "ABC Trading Co vs XYZ Enterprises" |

#### **📅 Demo Cause Lists**

**High Court (Delhi High Court):**
- 3 sample cases with complete details (judges, courtrooms, timings)
- Cases include WP, PIL, and CWP with realistic hearing schedules

**District Court (Tis Hazari):**
- 2 sample cases covering criminal and civil matters
- Complete case details with judge assignments and courtroom info

### **🧪 Testing Instructions**

1. **Case Search Testing:**
   - Go to `http://localhost:8081/court`
   - Enter any of the demo cases from the table above
   - View detailed case information with parties, dates, and status

2. **Cause List Testing:**
   - Navigate to `http://localhost:8081/court/cause-list`
   - Select "High Court of Delhi" or "District Court"
   - Choose any date to view demo cause list

3. **Error Handling Testing:**
   - Enter invalid case details (e.g., WP 9999/2020)
   - Observe user-friendly error messages

## 🔐 Configuration & Credentials

### **Environment Variables**

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./court_tracker.db

# Security
SECRET_KEY=your-secret-key-here

# Google Drive Integration (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integrations/google/callback

# AI Services (Optional)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key  
AI_ENABLED=true

# WhatsApp Integration (Optional)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# N8N Workflow (Optional)
N8N_WEBHOOK_URL=your-n8n-webhook-url

# Court Scraping Settings
SELENIUM_HEADLESS=true
SCRAPING_TIMEOUT=30
```

### **🔑 Credentials Setup**

#### **Required for Demo Mode:**
- **None** - Demo mode works without any credentials

#### **Required for Production Mode:**
1. **Database**: SQLite (included) or PostgreSQL URL
2. **Court API Access**: Some courts may require registration

#### **Optional Integrations:**
1. **Google Drive**: For document storage
   - Get credentials from [Google Cloud Console](https://console.cloud.google.com)
   
2. **AI Services**: For document analysis  
   - OpenAI API key for GPT integration
   - Anthropic API key for Claude integration

3. **WhatsApp Integration**: For notifications
   - Twilio Account SID and Auth Token
   - WhatsApp Business API access

4. **N8N Workflows**: For automation
   - N8N instance webhook URL

### **🛡️ Security Notes**
- Keep all API keys secure and never commit them to version control
- Use environment variables for all sensitive configuration
- The `.env.example` file shows required format without sensitive data
- Database is SQLite by default (file-based, no additional setup required)

## 🏗️ Architecture

### **Frontend (React + TypeScript)**
```
src/
├── components/        # Reusable UI components
├── pages/court/       # Court-specific pages
│   ├── CourtSearch.tsx
│   ├── CauseList.tsx
│   └── RecentSearches.tsx
├── lib/api.ts         # API integration
└── hooks/             # Custom React hooks
```

### **Backend (FastAPI + Python)**
```
backend/
├── app/
│   ├── routers/       # API endpoints
│   ├── services/      # Business logic
│   │   ├── court_scraper.py    # Web scraping engine
│   │   ├── pdf_generator.py    # PDF creation
│   │   └── cause_list_manager.py
│   ├── database.py    # SQLAlchemy models
│   └── schemas.py     # Pydantic models
└── static/           # File storage (PDFs, uploads)
```

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- Chrome browser (for Selenium scraping)

### **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Server runs on: `http://localhost:8000`

### **Frontend Setup**
```bash
npm install
npm run dev
```
Frontend runs on: `http://localhost:5173`

## 🔧 API Endpoints

### **Case Management**
- `POST /api/court/fetch-case` - Fetch case details from court portals
- `GET /api/court/recent-searches` - Retrieve recent search history
- `GET /api/court/download-judgment` - Download judgment/order PDFs

### **Cause List Management**  
- `GET /api/court/cause-list` - Get daily cause list entries
- `POST /api/court/fetch-causelist` - Fetch fresh cause list from court
- `GET /api/court/download-causelist` - Download cause list as PDF

### **Health & Monitoring**
- `GET /health` - Basic API health status
- `GET /api/health` - Detailed health check with database status

### **Integration APIs**
- `POST /api/whatsapp/send` - Send WhatsApp notifications
- `GET /api/drive/files` - List Google Drive files
- `POST /api/integrations/google/auth` - Google OAuth authentication

## 🐛 Troubleshooting Guide

### **Common Issues & Solutions**

#### **1. CORS Errors**
```
Error: Access blocked by CORS policy
```
**Solution**: Ensure frontend runs on allowed origin (localhost:8081 or localhost:5173)

#### **2. Backend Server Won't Start**
```
Error: Address already in use
```
**Solutions**:
- Check if port 8000 is in use: `netstat -ano | findstr :8000`
- Kill existing process or change port in server configuration
- Use the test server: `python test_server.py` instead of `python main.py`

#### **3. Frontend Build Errors**
```
Error: Cannot resolve module
```
**Solutions**:
- Delete `node_modules` and run `npm install` again
- Clear npm cache: `npm cache clean --force`
- Ensure Node.js version is 18+

#### **4. Database Connection Issues**
```
Error: Could not connect to database
```
**Solutions**:
- Check if `court_tracker.db` exists in backend directory
- Verify DATABASE_URL in .env file
- For SQLite, ensure write permissions in directory

#### **5. Case Search Returns "Not Found"**
**For Demo Mode**: Use exact demo cases from the table above
**For Production**: Verify court portal connectivity and case format

### **🔧 Development Tips**

#### **Hot Reloading Issues**
- Frontend: Save files to trigger Vite hot reload
- Backend: Use `--reload` flag with uvicorn for auto-restart

#### **Port Conflicts**
- Frontend will auto-select next available port (8081, 8082, etc.)
- Backend defaults to 8000, modify in server files if needed

#### **Database Reset**
```bash
# Delete existing database
rm backend/court_tracker.db

# Restart server to recreate tables
python test_server.py
```

## 🚀 Deployment Options

### **Local Development**
```bash
# Development with hot reload
npm run dev              # Frontend
python test_server.py    # Backend (demo mode)
```

### **Production Build**
```bash
# Build frontend for production
npm run build

# Serve built files
npm run preview

# Production backend
cd backend
python main.py
```

### **Docker Deployment** (Optional)
```dockerfile
# Dockerfile example for containerization
FROM node:18-alpine AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
COPY --from=frontend /app/dist ./static
CMD ["python", "main.py"]
```

### **Vercel Deployment** (Frontend Only)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
vercel --prod
```

**Environment Variables for Vercel:**
- `VITE_API_BASE_URL=https://your-backend-api.com`
- Backend needs separate deployment (Railway, Heroku, etc.)

## 🛡️ Error Handling

### **Robust Validation**
- Case number format validation
- Court type verification
- Date range validation
- Input sanitization

### **Graceful Degradation**
- Network timeout handling
- Scraping failure recovery
- Database connection errors
- User-friendly error messages

## 📁 Database Schema

### **case_queries**
```sql
- id (Primary Key)
- case_type, case_number, year
- court_type (high_court/district_court)
- parties, filing_date, next_hearing_date
- case_status, judgment_url
- raw_response (audit trail)
- success, error_message
- created_at, updated_at
```

### **cause_lists**
```sql
- id (Primary Key)
- court_type, date
- case_number, parties, hearing_type
- time, court_room, judge, status
- pdf_path (generated PDF location)
- created_at, updated_at
```

## 🔒 Security Features
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting on scraping requests
- Error message sanitization

## 📱 User Experience
- **Responsive Design** - Mobile and desktop friendly
- **Real-time Feedback** - Loading states and progress indicators  
- **Toast Notifications** - Success and error feedback
- **Local Storage** - Recent searches persistence
- **PDF Downloads** - Direct browser downloads

## 🧪 Testing
- Comprehensive test coverage removed for production
- API endpoint testing
- Web scraping validation
- Database integration tests
- Error handling verification

## � License
This project is developed for educational and legal research purposes in compliance with Indian court system guidelines.

- Search by case number, party names, lawyer names### ✅ UI - Simple Input Form

- Filter by court type (High Court, District Court)- **Case Type** selection dropdown

- Date range filtering for case filing- **Case Number** input field  

- Advanced search with multiple criteria- **Year** selection

- Clean, intuitive interface for legal professionals

### 📊 Data Visualization

- Search history tracking### ✅ Scraper/Fetcher

- Case statistics and analytics- **All High Courts & District Courts** in India via official eCourts portals

- Court-wise case distribution- **Comprehensive Data Parsing**:

  - ✅ Parties' names (Petitioner & Respondent)

## Technology Stack  - ✅ Filing date

  - ✅ Next hearing date  

### Frontend  - ✅ Case status (Pending/Disposed/etc.)

- **React 18** with TypeScript- **Judgment Downloads**: Automatically download judgments/orders as PDFs

- **Vite** for fast development and building- **Robust Error Handling**: Invalid case numbers, unavailable data

- **Tailwind CSS** with Shadcn/ui components

- **React Router** for navigation### ✅ Storage

- **React Query** for state management- **SQLite Database**: Stores each query and raw response

- **Query History**: Track all search requests

### Backend- **Response Caching**: Efficient data retrieval

- **FastAPI** with Python for high-performance APIs

- **SQLite** database for case data storage### ✅ Display

- **BeautifulSoup & Selenium** for web scraping- **Parsed Details Rendering**: Clean display of case information

- **Pandas** for data processing- **PDF Download Links**: Direct download of judgments/orders

- **Responsive Design**: Works on desktop and mobile

### Web Scraping

- Automated court portal scraping### ✅ Cause List Download

- eCourts portal integration- **Daily Cause Lists**: Cases listed for specific dates

- PDF download and processing- **Court-wise Filtering**: Filter by specific courts

- Data extraction and normalization- **PDF Export**: Download cause lists as PDF files



## Getting Started## 🚀 Quick Start



### Prerequisites### Frontend Setup

- Node.js 18+ and npm```bash

- Python 3.8+npm install

- Gitnpm run dev

```

### Installation

### Backend Setup

1. **Install frontend dependencies:**```bash

   ```bashcd backend

   npm installpip install -r requirements.txt

   ```uvicorn app.main:app --reload

```

2. **Install Python dependencies:**

   ```bash### Environment Setup

   cd backendCreate `.env` file:

   pip install -r requirements.txt```env

   ```DATABASE_URL=sqlite:///./court_cases.db

SELENIUM_HEADLESS=true

3. **Set up environment variables:**```

   ```bash

   cp .env.example .env## 🔍 Core Features

   # Edit .env with your configuration

   ```### Case Search Interface

- Simple form with Case Type, Case Number, Year inputs

4. **Initialize database:**- Real-time validation and error handling

   ```bash- Professional legal interface design

   python backend/init_db.py

   ```### Court Integration

- Connects to all High Courts and District Courts

### Running the Application- Scrapes official eCourts portals

- Handles different portal formats and structures

1. **Start the backend server:**

   ```bash### Data Extraction

   cd backend- Parses parties' names automatically

   python main.py- Extracts filing dates and hearing dates

   ```- Determines case status and progress

- Downloads judgment PDFs when available

2. **Start the frontend development server:**

   ```bash### Database Storage

   npm run dev- SQLite database for all queries and responses

   ```- Stores raw HTML responses for analysis

- Maintains search history for users

3. **Access the application:**- Caches frequently accessed case data

   - Frontend: http://localhost:8080

   - Backend API: http://localhost:8000## 📱 Usage



## Usage1. **Enter Case Details**: Use the form to input Case Type, Case Number, and Year

2. **Search**: Click search to fetch data from eCourts portals

### Case Search3. **View Results**: See parsed case details including parties, dates, and status

1. Navigate to the Court Search page4. **Download Judgments**: Click PDF links to download available judgments

2. Enter search criteria (case number, party names, etc.)5. **Access Cause Lists**: Use the cause list feature to get daily court listings

3. Select court type and jurisdiction

4. Review search results and access case details## 🏛️ Supported Courts



### Cause List Access- Supreme Court of India

1. Go to the Cause List section- All High Courts (Delhi, Bombay, Madras, Calcutta, etc.)

2. Select court and date- All District Courts across India

3. View scheduled cases for the selected date- Integration via official eCourts services

4. Download cause list in PDF format

## 🛠️ Technical Implementation

### Judgment Downloads

1. Search for cases using the search functionality### Frontend

2. Click on case details to view judgment information- React with TypeScript for type safety

3. Download available judgments in PDF format- Tailwind CSS for clean styling

- React Hook Form for form validation

## API Endpoints- Axios for API communication



### Court Search API### Backend

- `GET /api/courts/search` - Search for cases- FastAPI for high-performance API

- `GET /api/courts/cause-list` - Get cause list- BeautifulSoup4 for HTML parsing

- `GET /api/courts/recent` - Get recent searches- Selenium for dynamic content

- SQLite for data persistence

### Case Management API

- `GET /api/cases/{case_id}` - Get case details### Web Scraping

- `POST /api/cases/save` - Save case for later- Respectful scraping with rate limiting

- `GET /api/cases/saved` - Get saved cases- Multiple retry mechanisms

- Error recovery and fallback strategies

## Database Schema- Data validation and cleaning



### Cases Table## 📋 Project Structure

- case_id, case_number, court_name

- party_names, case_type, filing_date```

- status, last_hearing_datetask1/

├── src/

### Searches Table│   ├── components/

- search_id, query, filters│   │   ├── CaseSearchForm.tsx

- timestamp, results_count│   │   ├── CaseResults.tsx

│   │   └── CauseListDownloader.tsx

## Contributing│   ├── pages/

│   │   ├── SearchPage.tsx

1. Fork the repository│   │   └── HistoryPage.tsx

2. Create a feature branch│   └── services/

3. Make your changes│       └── api.ts

4. Add tests for new functionality├── backend/

5. Submit a pull request│   ├── app/

│   │   ├── services/

## License│   │   │   ├── court_scraper.py

│   │   │   └── pdf_downloader.py

This project is licensed under the MIT License - see the LICENSE file for details.│   │   ├── routers/

│   │   │   └── cases.py

## Support│   │   └── main.py

│   └── requirements.txt

For issues and questions:└── README.md

- Create an issue in the GitHub repository```

- Check the documentation in the `/docs` folder

- Review the API documentation at `/api/docs` when running## 📁 Project Structure

```
CourtLedger/
├── 📂 src/                          # Frontend React application
│   ├── 📂 components/               # Reusable UI components
│   │   ├── Navigation.tsx           # App navigation
│   │   └── 📂 ui/                   # shadcn/ui components
│   ├── 📂 pages/                    # Page components
│   │   ├── Home.tsx                 # Landing page
│   │   └── 📂 court/                # Court-related pages
│   │       ├── CourtSearch.tsx      # Case search interface
│   │       └── CauseList.tsx        # Cause list viewer
│   ├── 📂 lib/                      # Utilities and API client
│   │   ├── api.ts                   # Axios API client
│   │   └── utils.ts                 # Helper functions
│   └── 📂 hooks/                    # Custom React hooks
├── 📂 backend/                      # FastAPI backend server
│   ├── 📂 app/                      # Application core
│   │   ├── 📂 routers/              # API route handlers
│   │   │   ├── court.py             # Court case endpoints
│   │   │   ├── drive.py             # Google Drive integration
│   │   │   └── whatsapp.py          # WhatsApp integration
│   │   ├── 📂 services/             # Business logic
│   │   │   ├── court_scraper.py     # Web scraping logic
│   │   │   ├── demo_data.py         # Mock data service
│   │   │   └── pdf_generator.py     # PDF generation
│   │   ├── database.py              # SQLAlchemy models
│   │   ├── config.py                # Configuration management
│   │   └── schemas.py               # Pydantic schemas
│   ├── main.py                      # Production server entry
│   ├── requirements.txt             # Python dependencies
│   └── 📂 static/                   # Static files (PDFs, etc.)
├── test_server.py                   # Demo server with mock data
├── package.json                     # Node.js dependencies
├── vite.config.ts                   # Vite configuration
├── tailwind.config.ts               # Tailwind CSS config
└── 📄 README.md                     # This file
```

## 🤝 Contributing

We welcome contributions to CourtLedger! Here's how you can help:

### **🔀 Getting Started**
1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes and test thoroughly
5. **Commit** with clear messages: `git commit -m 'Add amazing feature'`
6. **Push** to your fork: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request with detailed description

### **🐛 Reporting Issues**
- Use GitHub Issues for bug reports
- Include steps to reproduce the issue
- Provide system information (OS, Python/Node versions)
- Screenshots for UI issues

### **💡 Feature Requests**
- Check existing issues before creating new ones
- Clearly describe the proposed feature
- Explain the use case and benefits

### **🧪 Development Guidelines**
- Write tests for new features
- Follow existing code style and conventions
- Update documentation for API changes
- Ensure both demo and production modes work

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Indian Judiciary** for providing public access to court data
- **eCourts Portal** for digital case information systems
- **React & FastAPI Communities** for excellent frameworks
- **shadcn/ui** for beautiful, accessible UI components
- **Tailwind CSS** for utility-first styling
- **Open Source Community** for libraries and inspiration

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs and request features](https://github.com/Mythripaluri/CourtLedger/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/Mythripaluri/CourtLedger/discussions)
- **Documentation**: API docs available at `/docs` when server is running
- **Email**: For private inquiries (check GitHub profile)

---

**🎯 Perfect for demonstrating:** Web scraping, legal tech integration, modern full-stack development, API design, and real-world problem solving! 🚀

### **⭐ If this project helps you, please give it a star on GitHub!**