# Court-Data Fetcher & Judgement Downloader

![Indian Courts](https://img.shields.io/badge/Indian-Courts-orange)
![eCourts](https://img.shields.io/badge/eCourts-Integration-green)
![Web Scraping](https://img.shields.io/badge/Web-Scraping-blue)
![PDF Download](https://img.shields.io/badge/PDF-Download-red)

## 🎯 Project Objective

A comprehensive web application that allows users to enter Case Type, Case Number, and Year for Indian courts, fetches case details, downloads judgments/orders, and provides cause list functionality for daily case listings.

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
- `POST /api/court/fetch-case` - Fetch case details
- `GET /api/court/recent-searches` - Get recent searches
- `GET /api/court/download-judgment` - Download judgment PDF

### **Cause List Management**
- `POST /api/court/fetch-causelist` - Fetch daily cause list
- `GET /api/court/download-causelist` - Download cause list PDF
- `GET /api/court/cause-list` - Get stored cause list entries

### **Health Checks**
- `GET /health` - API health status
- `GET /api/health` - Detailed health check

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

- Review the API documentation at `/api/docs` when runningPerfect for demonstrating web scraping, data processing, and legal tech integration skills! 🚀


## Deployment

### Production Build
```bash
npm run build
```

### Docker Deployment
```bash
docker build -t court-data-fetcher .
docker run -p 8080:8080 court-data-fetcher
```

## Acknowledgments

- Indian Judiciary for providing public access to court data
- eCourts portal for case information
- Open source community for excellent libraries and tools