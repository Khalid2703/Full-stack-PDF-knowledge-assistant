"""
Pydantic schemas for Chat-related requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """Request to send a chat message"""
    session_id: str
    message: str
    file_ids: Optional[List[int]] = None  # Specific files to search
    use_rag: bool = Field(default=True)


class SourceReference(BaseModel):
    """Reference to a source chunk"""
    file_id: int
    filename: str
    chunk_index: int
    page_number: Optional[int]
    relevance_score: float
    content_preview: str  # First 200 chars


class ChatResponse(BaseModel):
    """Response with assistant message and sources"""
    message: str
    sources: List[SourceReference]
    session_id: str
    created_at: datetime


class ChatHistory(BaseModel):
    """Chat conversation history"""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
