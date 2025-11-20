"""
Chat model for storing conversation history
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)  # Group related messages
    
    # Message content
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # RAG context
    sources = Column(JSON, nullable=True)  # List of source chunks/files used
    relevance_scores = Column(JSON, nullable=True)  # Scores for retrieved chunks
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, session={self.session_id}, role={self.role})>"
