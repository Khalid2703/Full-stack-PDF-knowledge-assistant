"""
Test script for web scraping
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.web_service import web_service
from app.utils.logger import app_logger


def test_scraping(url: str):
    """Test web scraping"""
    try:
        app_logger.info(f"Testing web scraping: {url}")
        
        result = web_service.scrape_url(url)
        
        app_logger.info(f"✅ Scraping successful!")
        app_logger.info(f"   Title: {result['title']}")
        app_logger.info(f"   Content length: {result['content_length']} characters")
        app_logger.info(f"   Metadata: {result['metadata']}")
        app_logger.info(f"   First 200 chars: {result['content'][:200]}")
        
    except Exception as e:
        app_logger.error(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        test_scraping(url)
    else:
        app_logger.info("Usage: python test_web_scraping.py <url>")
