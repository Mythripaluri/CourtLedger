from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from backend.app.database import engine, Base
from backend.app.routers import court, drive, integrations, whatsapp, n8n_integration
from backend.app.config import settings

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Court Case Tracker & Drive Assistant API",
    description="Backend API for managing court cases and WhatsApp Google Drive integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for PDFs and downloads
import os
static_dir = os.path.join(os.path.dirname(__file__), "backend", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(court.router, prefix="/api/court", tags=["Court Case Tracker"])
app.include_router(drive.router, prefix="/api/drive", tags=["Google Drive"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp Assistant"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(n8n_integration.router, tags=["N8N Workflow Automation"])

@app.get("/")
async def root():
    return {"message": "Court Case Tracker & Drive Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main_backend:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )