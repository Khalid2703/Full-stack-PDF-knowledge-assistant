"""
Database initialization script
Creates all tables and optionally seeds data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base, engine
from app.models import User, File, Chunk, Chat
from app.utils.logger import app_logger


def init_database():
    """Initialize database tables"""
    try:
        app_logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        app_logger.info("✅ Database tables created successfully!")
        
    except Exception as e:
        app_logger.error(f"❌ Error creating tables: {str(e)}")
        raise


if __name__ == "__main__":
    init_database()
