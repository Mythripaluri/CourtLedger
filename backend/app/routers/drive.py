from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db, FileSummary
from ..schemas import (
    DriveListResponse, DriveFile, FileSummaryRequest, 
    FileSummaryResponse, DriveCommandResponse
)
from ..services.drive_service import GoogleDriveService
from ..services.ai_service import AIService

router = APIRouter()

@router.get("/files", response_model=DriveListResponse)
async def get_drive_files(
    folder_path: str = "/",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get files in Google Drive folder"""
    return await list_drive_files(folder_path, limit, db)

@router.get("/list", response_model=DriveListResponse)
async def list_drive_files(
    folder_path: str = "/",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List files in Google Drive folder
    """
    try:
        drive_service = GoogleDriveService()
        files = await drive_service.list_files(folder_path, limit)
        
        drive_files = []
        for file in files:
            drive_files.append(DriveFile(
                id=file["id"],
                name=file["name"],
                type=file["type"],
                size=file.get("size"),
                modified_time=file.get("modified_time"),
                web_view_link=file.get("web_view_link")
            ))
        
        return DriveListResponse(
            files=drive_files,
            folder_path=folder_path,
            total_files=len(drive_files)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.delete("/delete")
async def delete_drive_file(
    file_path: str,
    db: Session = Depends(get_db)
):
    """
    Delete a file from Google Drive
    """
    try:
        drive_service = GoogleDriveService()
        result = await drive_service.delete_file(file_path)
        
        if result:
            return {"status": "success", "message": f"Successfully deleted {file_path}"}
        else:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.post("/move")
async def move_drive_file(
    source_path: str,
    dest_path: str,
    db: Session = Depends(get_db)
):
    """
    Move a file in Google Drive
    """
    try:
        drive_service = GoogleDriveService()
        result = await drive_service.move_file(source_path, dest_path)
        
        if result:
            return {"status": "success", "message": f"Successfully moved {source_path} to {dest_path}"}
        else:
            raise HTTPException(status_code=404, detail="File not found or could not be moved")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to move file: {str(e)}")

@router.post("/rename")
async def rename_drive_file(
    file_path: str,
    new_name: str,
    db: Session = Depends(get_db)
):
    """
    Rename a file in Google Drive
    """
    try:
        drive_service = GoogleDriveService()
        result = await drive_service.rename_file(file_path, new_name)
        
        if result:
            return {"status": "success", "message": f"Successfully renamed {file_path} to {new_name}"}
        else:
            raise HTTPException(status_code=404, detail="File not found or could not be renamed")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename file: {str(e)}")

@router.post("/upload")
async def upload_file_to_drive(
    folder_path: str = "/",
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file to Google Drive
    """
    try:
        drive_service = GoogleDriveService()
        
        # Read file content
        content = await file.read()
        
        result = await drive_service.upload_file(
            folder_path=folder_path,
            filename=file.filename,
            content=content,
            content_type=file.content_type
        )
        
        if result:
            return {"status": "success", "message": f"Successfully uploaded {file.filename} to {folder_path}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to upload file")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/summary", response_model=FileSummaryResponse)
async def generate_file_summary(
    request: FileSummaryRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI summary of a file
    """
    try:
        # Check if summary already exists
        existing_summary = db.query(FileSummary).filter(
            FileSummary.file_id == request.file_id
        ).first()
        
        if existing_summary:
            return FileSummaryResponse(
                file_id=existing_summary.file_id,
                file_name=existing_summary.file_name,
                summary=existing_summary.summary_text,
                ai_model=existing_summary.ai_model,
                created_at=existing_summary.created_at
            )
        
        # Download file content
        drive_service = GoogleDriveService()
        content = await drive_service.download_file_content(request.file_id)
        
        if not content:
            raise HTTPException(status_code=404, detail="File not found or could not be downloaded")
        
        # Generate summary
        ai_service = AIService()
        summary = await ai_service.summarize_text(content, request.file_path)
        
        # Get file details
        file_details = await drive_service.get_file_details(request.file_id)
        
        # Save summary to database
        file_summary = FileSummary(
            file_id=request.file_id,
            file_name=file_details.get("name", "Unknown"),
            file_path=request.file_path,
            file_type=file_details.get("type", "unknown"),
            summary_text=summary,
            ai_model=request.use_ai_model,
            file_size=file_details.get("size", 0)
        )
        
        db.add(file_summary)
        db.commit()
        db.refresh(file_summary)
        
        return FileSummaryResponse(
            file_id=file_summary.file_id,
            file_name=file_summary.file_name,
            summary=file_summary.summary_text,
            ai_model=file_summary.ai_model,
            created_at=file_summary.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/summary/{file_id}", response_model=FileSummaryResponse)
async def get_file_summary(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Get existing file summary
    """
    try:
        file_summary = db.query(FileSummary).filter(
            FileSummary.file_id == file_id
        ).first()
        
        if not file_summary:
            raise HTTPException(status_code=404, detail="File summary not found")
        
        return FileSummaryResponse(
            file_id=file_summary.file_id,
            file_name=file_summary.file_name,
            summary=file_summary.summary_text,
            ai_model=file_summary.ai_model,
            created_at=file_summary.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file summary: {str(e)}")

@router.get("/search")
async def search_drive_files(
    query: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search files in Google Drive
    """
    try:
        drive_service = GoogleDriveService()
        files = await drive_service.search_files(query, limit)
        
        drive_files = []
        for file in files:
            drive_files.append(DriveFile(
                id=file["id"],
                name=file["name"],
                type=file["type"],
                size=file.get("size"),
                modified_time=file.get("modified_time"),
                web_view_link=file.get("web_view_link")
            ))
        
        return {
            "query": query,
            "files": drive_files,
            "total_results": len(drive_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search files: {str(e)}")