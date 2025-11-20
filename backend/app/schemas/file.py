"""
Pydantic schemas for File-related requests and responses
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class FileMetadata(BaseModel):
    """Extracted metadata from files"""
    title: Optional[str] = None
    author: Optional[str] = None
    page_count: Optional[int] = None
    created_date: Optional[datetime] = None
    toc: Optional[List[dict]] = None  # Table of contents
    entities: Optional[List[str]] = None  # Named entities


class FileUploadResponse(BaseModel):
    """Response after file upload"""
    file_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    upload_status: str
    metadata: Optional[FileMetadata] = None
    
    class Config:
        from_attributes = True


class URLScrapeRequest(BaseModel):
    """Request to scrape a URL"""
    url: HttpUrl
    extract_metadata: bool = Field(default=True)


class URLScrapeResponse(BaseModel):
    """Response after URL scraping"""
    file_id: int
    url: str
    title: Optional[str]
    content_length: int
    scrape_status: str
    metadata: Optional[FileMetadata] = None


class FileListResponse(BaseModel):
    """Response for listing user files"""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: Optional[int]
    page_count: Optional[int]
    is_processed: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class SmartSectionView(BaseModel):
    """Enhanced metadata view for files"""
    file_id: int
    title: Optional[str]
    author: Optional[str]
    page_count: Optional[int]
    table_of_contents: Optional[List[dict]]
    key_entities: Optional[List[str]]
    summary: Optional[str]
    word_count: int
    chunk_count: int
