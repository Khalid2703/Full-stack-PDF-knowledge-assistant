"""
Test script for PDF extraction
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.pdf_service import pdf_service
from app.utils.logger import app_logger


def test_pdf_extraction(pdf_path: str):
    """Test PDF text extraction"""
    try:
        if not os.path.exists(pdf_path):
            app_logger.error(f"❌ File not found: {pdf_path}")
            return
        
        app_logger.info(f"Testing PDF extraction: {pdf_path}")
        
        # Extract text
        result = pdf_service.extract_text(pdf_path)
        
        app_logger.info(f"✅ Extraction successful!")
        app_logger.info(f"   Pages: {result['page_count']}")
        app_logger.info(f"   Total text length: {len(result['full_text'])} characters")
        app_logger.info(f"   Metadata: {result['metadata']}")
        
        # Extract TOC
        toc = pdf_service.extract_toc(pdf_path)
        app_logger.info(f"   TOC entries: {len(toc)}")
        
        if toc:
            app_logger.info("   First 3 TOC entries:")
            for entry in toc[:3]:
                app_logger.info(f"      - {entry['title']} (Page {entry['page']})")
        
    except Exception as e:
        app_logger.error(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        test_pdf_extraction(pdf_path)
    else:
        app_logger.info("Usage: python test_pdf.py <path_to_pdf>")
