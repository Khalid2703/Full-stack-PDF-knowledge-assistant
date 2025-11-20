"""
Routes package initialization
Updated for DAY 2 with chat_v2 and automations
"""

from app.routes import auth, upload, scrape, chat, automations
from app.routes import chat_v2

__all__ = ["auth", "upload", "scrape", "chat", "chat_v2", "automations"]
