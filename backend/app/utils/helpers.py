"""
General utility functions
"""

import os
import uuid
from typing import List
from datetime import datetime


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename preserving extension"""
    ext = os.path.splitext(original_filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name


def allowed_file(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(filepath)


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Overlap between consecutive chunks
    
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    
    return chunks
