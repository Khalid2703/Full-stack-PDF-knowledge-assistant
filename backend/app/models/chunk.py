"""
Chunk model for storing text embeddings and vector representations
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, PickleType
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order in document
    content = Column(Text, nullable=False)  # The actual text chunk
    
    # Metadata
    page_number = Column(Integer, nullable=True)  # For PDFs
    section_title = Column(String(500), nullable=True)  # From TOC
    
    # Embedding vector (stored as pickle for simplicity, use pgvector in production)
    embedding_vector = Column(PickleType, nullable=True)
    vector_id = Column(String(255), nullable=True)  # ID in FAISS/Chroma
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship("File", back_populates="chunks")
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, file_id={self.file_id}, index={self.chunk_index})>"
