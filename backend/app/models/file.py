"""
File model for uploaded PDFs and scraped web content
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, url
    file_path = Column(String(1000), nullable=True)  # Path for uploaded files
    url = Column(Text, nullable=True)  # Original URL for scraped content
    file_size = Column(Integer, nullable=True)  # Size in bytes
    page_count = Column(Integer, nullable=True)  # For PDFs
    
    # Metadata
    title = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    created_date = Column(DateTime, nullable=True)
    
    # Processing status
    is_processed = Column(Integer, default=0)  # 0=pending, 1=processing, 2=completed, 3=failed
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="files")
    chunks = relationship("Chunk", back_populates="file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, type={self.file_type})>"
