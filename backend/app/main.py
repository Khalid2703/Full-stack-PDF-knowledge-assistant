"""
FastAPI main application entry point
Configures middleware, routes, and startup events
DAY 2: Enhanced with SSE, Rate Limiting, and Automation
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.utils.logger import app_logger
from app.routes import auth, upload, scrape, chat, chat_v2, automations


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    app_logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    app_logger.info(f"   Environment: {settings.ENVIRONMENT}")
    app_logger.info(f"   RAG Mode: {settings.RAG_MODE}")
    app_logger.info(f"   Reranking: {'Enabled' if settings.RAG_RERANK else 'Disabled'}")
    
    # Initialize database
    try:
        init_db()
        app_logger.info("✅ Database initialized successfully")
    except Exception as e:
        app_logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise
    
    # Check Gemini API
    if settings.GEMINI_API_KEY:
        app_logger.info("✅ Gemini API configured")
    else:
        app_logger.warning("⚠️ Gemini API key not configured")
    
    yield
    
    # Shutdown
    app_logger.info("👋 Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Universal PDF + Web Knowledge Assistant with RAG, SSE Streaming, and Automation",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# CORS Middleware - Configure allowed origins from environment
cors_origins_list = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
if "*" in cors_origins_list or len(cors_origins_list) == 0:
    cors_origins_list = ["*"]
    if settings.ENVIRONMENT == "production":
        app_logger.warning("⚠️ CORS allows all origins in production. Consider setting CORS_ORIGINS environment variable.")

app_logger.info(f"🌐 CORS configured for origins: {cors_origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(scrape.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(chat_v2.router, prefix="/api")  # Enhanced Chat V2
app.include_router(automations.router, prefix="/api")  # Automations


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    app_logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    app_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
@limiter.limit("100/minute")
async def health_check(request: Request):
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "rag_mode": settings.RAG_MODE,
        "features": {
            "sse_streaming": True,
            "reranking": settings.RAG_RERANK,
            "safety_guards": {
                "prompt_injection": settings.ENABLE_PROMPT_INJECTION_GUARD,
                "hallucination": settings.ENABLE_HALLUCINATION_GUARD
            },
            "automations": {
                "gmail": bool(settings.GMAIL_EMAIL),
                "whatsapp": bool(settings.***REMOVED***_ACCOUNT_SID),
                "push": bool(settings.ONESIGNAL_APP_ID)
            }
        }
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/health",
        "features": {
            "chat": "RAG-powered chat with streaming",
            "chat_v2": "Enhanced chat with dual RAG modes",
            "safety": "Prompt injection & hallucination guards",
            "automation": "Gmail, WhatsApp, Push notifications",
            "rag_modes": ["fast", "accurate"],
            "powered_by": "Google Gemini API (Free)"
        }
    }


# Configuration endpoint
@app.get("/api/config", tags=["Configuration"])
async def get_config():
    """
    Get public configuration
    """
    return {
        "rag_mode": settings.RAG_MODE,
        "top_k": settings.RAG_TOP_K,
        "reranking_enabled": settings.RAG_RERANK,
        "max_file_size": settings.MAX_FILE_SIZE,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS.split(','),
        "features": {
            "streaming": True,
            "safety_guards": True,
            "automations": True,
            "dual_rag_modes": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
