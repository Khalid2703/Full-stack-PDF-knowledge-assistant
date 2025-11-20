"""
File upload routes for PDF processing
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from app.database import get_db, SessionLocal
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.file import File as FileModel
from app.models.chunk import Chunk
from app.schemas.file import FileUploadResponse, FileListResponse, SmartSectionView, FileMetadata
from app.services.pdf_service import pdf_service
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service
from app.services.metadata_service import metadata_service
from app.utils.helpers import generate_unique_filename, allowed_file, get_file_size, chunk_text
from app.utils.logger import app_logger
from app.config import settings


router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/pdf", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a PDF file for processing
    
    - Extracts text (with OCR fallback for scanned PDFs)
    - Generates embeddings
    - Stores in vector database
    - Extracts metadata and TOC
    """
    try:
        # Validate file type
        allowed_extensions = settings.ALLOWED_EXTENSIONS.split(',')
        if not allowed_file(file.filename, allowed_extensions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = get_file_size(file_path)
        
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1000000}MB"
            )
        
        # Create file record (processing will happen in background)
        file_record = FileModel(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_type="pdf",
            file_path=file_path,
            file_size=file_size,
            is_processed=1  # Processing
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        # Schedule background processing to avoid request cancellation
        def process_file_background(file_id: int, path: str):
            db_bg = SessionLocal()
            try:
                # Re-query the file record in background session
                file_rec = db_bg.query(FileModel).filter(FileModel.id == file_id).first()

                app_logger.info(f"Background: Extracting text from PDF id={file_id} path={path}")
                extraction_result = pdf_service.extract_text(path)
                toc = pdf_service.extract_toc(path)

                # Update file metadata
                file_rec.page_count = extraction_result['page_count']
                file_rec.title = extraction_result['metadata'].get('title') or file_rec.original_filename
                file_rec.author = extraction_result['metadata'].get('author')

                full_text = extraction_result['full_text']
                text_chunks = chunk_text(full_text, chunk_size=1000, overlap=200)

                app_logger.info(f"Background: Created {len(text_chunks)} chunks for file id={file_id}")

                chunk_records = []
                for idx, chunk_text_content in enumerate(text_chunks):
                    page_num = None
                    for page_data in extraction_result['page_texts']:
                        if chunk_text_content[:100] in page_data['text']:
                            page_num = page_data['page_number']
                            break

                    chunk_record = Chunk(
                        file_id=file_rec.id,
                        chunk_index=idx,
                        content=chunk_text_content,
                        page_number=page_num
                    )
                    db_bg.add(chunk_record)
                    chunk_records.append(chunk_record)

                db_bg.commit()

                for chunk_record in chunk_records:
                    db_bg.refresh(chunk_record)

                # Prepare for vector store
                chunk_data_list = []
                for chunk_record in chunk_records:
                    chunk_data_list.append({
                        'file_id': file_rec.id,
                        'chunk_id': chunk_record.id,
                        'chunk_index': chunk_record.chunk_index,
                        'content': chunk_record.content,
                        'page_number': chunk_record.page_number,
                        'filename': file_rec.original_filename
                    })

                app_logger.info(f"Background: Adding chunks to vector store for file id={file_id}")
                try:
                    vector_ids = rag_service.add_documents(chunk_data_list)
                except Exception as e:
                    app_logger.error(f"Background: Embedding/vector error for file id={file_id}: {e}")
                    vector_ids = []

                # Update chunk records with vector ids if available
                if vector_ids:
                    for chunk_record, vector_id in zip(chunk_records, vector_ids):
                        chunk_record.vector_id = str(vector_id)

                # Mark processed
                file_rec.is_processed = 2
                file_rec.processed_at = datetime.utcnow()
                db_bg.commit()

                # Optionally extract entities and other metadata (non-blocking)
                try:
                    metadata_service.extract_entities(full_text[:5000])
                except Exception:
                    pass

                app_logger.info(f"Background: Successfully processed file id={file_id}")

            except Exception as e:
                db_bg.rollback()
                try:
                    file_fail = db_bg.query(FileModel).filter(FileModel.id == file_id).first()
                    if file_fail:
                        file_fail.is_processed = 3
                        file_fail.processing_error = str(e)
                        db_bg.commit()
                except Exception:
                    pass
                app_logger.error(f"Background processing failed for file id={file_id}: {str(e)}")
            finally:
                db_bg.close()

        # Add to background tasks
        if background_tasks is not None:
            background_tasks.add_task(process_file_background, file_record.id, file_path)

        app_logger.info(f"Scheduled background processing for file id={file_record.id}")

        # Return immediate response indicating processing started
        return FileUploadResponse(
            file_id=file_record.id,
            filename=file_record.filename,
            original_filename=file_record.original_filename,
            file_type=file_record.file_type,
            file_size=file_record.file_size,
            upload_status="processing",
            metadata=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )


@router.get("/files", response_model=List[FileListResponse])
async def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all files uploaded by current user
    """
    files = db.query(FileModel).filter(FileModel.user_id == current_user.id).all()
    return files


@router.get("/files/{file_id}/status")
async def get_file_status(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return processing status for a file
    """
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()

    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return {
        "file_id": file.id,
        "is_processed": file.is_processed,
        "processing_error": file.processing_error,
        "processed_at": file.processed_at
    }


@router.get("/files/{file_id}/metadata", response_model=SmartSectionView)
async def get_file_metadata(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get enhanced metadata for a specific file (Smart Sections View)
    """
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Get all chunks for this file
    chunks = db.query(Chunk).filter(Chunk.file_id == file_id).all()
    
    # Combine chunk content
    full_text = "\n\n".join([chunk.content for chunk in chunks])
    
    # Extract TOC if PDF
    toc = []
    if file.file_type == "pdf" and file.file_path:
        toc = pdf_service.extract_toc(file.file_path)
    
    # Analyze document
    analysis = metadata_service.analyze_document(full_text, toc)
    
    return SmartSectionView(
        file_id=file.id,
        title=file.title,
        author=file.author,
        page_count=file.page_count,
        table_of_contents=toc,
        key_entities=analysis.get('entities', []),
        summary=analysis.get('summary', ''),
        word_count=analysis.get('word_count', 0),
        chunk_count=len(chunks)
    )


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file and all associated chunks and vectors
    """
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete from vector store
        rag_service.delete_file_vectors(file_id)
        
        # Delete physical file
        if file.file_path and os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        # Delete from database (cascades to chunks)
        db.delete(file)
        db.commit()
        
        app_logger.info(f"Deleted file: {file.filename}")
        return {"message": "File deleted successfully"}
    
    except Exception as e:
        db.rollback()
        app_logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
