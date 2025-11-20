"""
Web scraping routes for URL content extraction
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.file import File as FileModel
from app.models.chunk import Chunk
from app.schemas.file import URLScrapeRequest, URLScrapeResponse, FileMetadata
from app.services.web_service import web_service
from app.services.rag_service import rag_service
from app.services.metadata_service import metadata_service
from app.utils.helpers import chunk_text
from app.utils.logger import app_logger


router = APIRouter(prefix="/scrape", tags=["Web Scraping"])


@router.post("/url", response_model=URLScrapeResponse, status_code=status.HTTP_201_CREATED)
async def scrape_url(
    request: URLScrapeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scrape content from a URL
    
    - Extracts main content from webpage
    - Converts to clean markdown
    - Generates embeddings
    - Stores in vector database
    """
    try:
        # Scrape the URL
        app_logger.info(f"Scraping URL: {request.url}")
        scrape_result = web_service.scrape_url(str(request.url))
        
        # Create file record
        file_record = FileModel(
            user_id=current_user.id,
            filename=scrape_result['title'][:200],  # Truncate long titles
            original_filename=scrape_result['title'],
            file_type="url",
            url=str(request.url),
            title=scrape_result['title'],
            author=scrape_result['metadata'].get('author'),
            is_processed=1  # Processing
        )
        
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        
        try:
            # Chunk the content
            content = scrape_result['content']
            text_chunks = chunk_text(content, chunk_size=1000, overlap=200)
            
            app_logger.info(f"Created {len(text_chunks)} chunks from URL content")
            
            # Create chunk records
            chunk_data_list = []
            chunk_records = []
            
            for idx, chunk_text_content in enumerate(text_chunks):
                chunk_record = Chunk(
                    file_id=file_record.id,
                    chunk_index=idx,
                    content=chunk_text_content
                )
                
                db.add(chunk_record)
                chunk_records.append(chunk_record)
            
            db.commit()
            
            # Refresh to get IDs
            for chunk_record in chunk_records:
                db.refresh(chunk_record)
            
            # Prepare data for vector store
            for chunk_record in chunk_records:
                chunk_data_list.append({
                    'file_id': file_record.id,
                    'chunk_id': chunk_record.id,
                    'chunk_index': chunk_record.chunk_index,
                    'content': chunk_record.content,
                    'filename': scrape_result['title']
                })
            
            # Add to vector store
            app_logger.info("Adding chunks to vector store")
            vector_ids = rag_service.add_documents(chunk_data_list)
            
            # Update chunk records with vector IDs
            for chunk_record, vector_id in zip(chunk_records, vector_ids):
                chunk_record.vector_id = str(vector_id)
            
            # Mark as processed
            file_record.is_processed = 2  # Completed
            file_record.processed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(file_record)
            
            # Generate metadata if requested
            metadata = None
            if request.extract_metadata:
                metadata = FileMetadata(
                    title=scrape_result['title'],
                    author=scrape_result['metadata'].get('author'),
                    entities=metadata_service.extract_entities(content[:5000])
                )
            
            app_logger.info(f"Successfully scraped URL: {request.url}")
            
            return URLScrapeResponse(
                file_id=file_record.id,
                url=str(request.url),
                title=scrape_result['title'],
                content_length=len(content),
                scrape_status="completed",
                metadata=metadata
            )
        
        except Exception as e:
            # Mark as failed
            file_record.is_processed = 3  # Failed
            file_record.processing_error = str(e)
            db.commit()
            
            app_logger.error(f"Error processing scraped content: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing content: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Scraping error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape URL: {str(e)}"
        )
