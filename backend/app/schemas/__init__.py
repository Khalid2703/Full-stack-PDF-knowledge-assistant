"""
Schemas package initialization
"""

from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, TokenData
)
from app.schemas.file import (
    FileUploadResponse, URLScrapeRequest, URLScrapeResponse,
    FileListResponse, SmartSectionView, FileMetadata
)
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatHistory, SourceReference, ChatMessage
)

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
    "FileUploadResponse", "URLScrapeRequest", "URLScrapeResponse",
    "FileListResponse", "SmartSectionView", "FileMetadata",
    "ChatRequest", "ChatResponse", "ChatHistory", "SourceReference", "ChatMessage"
]
