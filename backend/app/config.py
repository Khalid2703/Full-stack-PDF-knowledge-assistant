"""
Configuration management using Pydantic Settings
Loads environment variables and provides type-safe configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = Field(default="Regnova Knowledge Assistant")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    CORS_ORIGINS: str = Field(default="*")  # Comma-separated list of allowed origins
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./regnova.db")
    
    # JWT Authentication
    SECRET_KEY: str = Field(default="change-this-secret-key")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # Google Gemini API (FREE)
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    # OpenAI
    ***REMOVED***_API_KEY: Optional[str] = Field(default=None)
    
    # File Storage
    UPLOAD_DIR: str = Field(default="./storage/uploads")
    MAX_FILE_SIZE: int = Field(default=50000000)  # 50MB
    ALLOWED_EXTENSIONS: str = Field(default="pdf,txt,doc,docx")
    
    # Vector Store
    VECTOR_STORE_TYPE: str = Field(default="faiss")
    VECTOR_STORE_PATH: str = Field(default="./storage/vector_store")
    
    # Embedding Configuration (Gemini)
    EMBEDDING_MODEL: str = Field(default="models/embedding-001")
    EMBEDDING_DIMENSION: int = Field(default=768)
    
    # LLM Configuration (Gemini)
    LLM_MODEL: str = Field(default="gemini-pro")
    LLM_TEMPERATURE: float = Field(default=0.7)
    LLM_MAX_TOKENS: int = Field(default=2048)
    
    # RAG Configuration
    RAG_TOP_K: int = Field(default=5)
    RAG_RERANK: bool = Field(default=True)
    RAG_MODE: str = Field(default="accurate")  # fast or accurate
    
    # OCR
    TESSERACT_CMD: Optional[str] = Field(default=None)
    
    # Web Scraping
    USER_AGENT: str = Field(default="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    REQUEST_TIMEOUT: int = Field(default=30)
    
    # Gmail Automation
    GMAIL_SMTP_SERVER: str = Field(default="smtp.gmail.com")
    GMAIL_SMTP_PORT: int = Field(default=587)
    GMAIL_EMAIL: Optional[str] = Field(default=None)
    GMAIL_APP_PASSWORD: Optional[str] = Field(default=None)
    
    # ***REMOVED*** WhatsApp
    ***REMOVED***_ACCOUNT_SID: Optional[str] = Field(default=None)
    ***REMOVED***_***REMOVED***: Optional[str] = Field(default=None)
    ***REMOVED***_WHATSAPP_FROM: Optional[str] = Field(default=None)
    ***REMOVED***_WHATSAPP_TO: Optional[str] = Field(default=None)
    
    # OneSignal Push Notifications
    ONESIGNAL_APP_ID: Optional[str] = Field(default=None)
    ONESIGNAL_REST_API_KEY: Optional[str] = Field(default=None)
    
    # Web Push VAPID
    VAPID_PUBLIC_KEY: Optional[str] = Field(default=None)
    VAPID_PRIVATE_KEY: Optional[str] = Field(default=None)
    VAPID_ADMIN_EMAIL: Optional[str] = Field(default=None)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_PER_MINUTE: int = Field(default=10)
    
    # Safety Features
    ENABLE_PROMPT_INJECTION_GUARD: bool = Field(default=True)
    ENABLE_HALLUCINATION_GUARD: bool = Field(default=True)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="./logs/app.log")

    # OpenAI model selection (optional)
    ENABLE_RAPTOR_MINI: bool = Field(default=True)
    DEFAULT_CHAT_MODEL: str = Field(default="raptor-mini")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.VECTOR_STORE_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)

        # Backwards-compatibility: ensure DEFAULT_CHAT_MODEL is set when raptor is enabled
        if getattr(self, "ENABLE_RAPTOR_MINI", False) and (not getattr(self, "DEFAULT_CHAT_MODEL", None)):
            self.DEFAULT_CHAT_MODEL = "raptor-mini"


# Global settings instance
settings = Settings()
