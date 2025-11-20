"""
PDF extraction service with OCR fallback
Uses PyMuPDF for text extraction and Tesseract for scanned PDFs
"""

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
from typing import Dict, List, Optional
from app.utils.logger import app_logger
from app.config import settings


class PDFService:
    """Service for extracting text and metadata from PDF files"""
    
    def __init__(self):
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    
    def extract_text(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract text from PDF with OCR fallback for scanned documents
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dictionary containing text, page_count, and metadata
        """
        doc = None
        try:
            doc = fitz.open(pdf_path)
            full_text = []
            page_texts = []

            page_count = len(doc)

            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text()

                # If page has minimal text, use OCR
                if len(text.strip()) < 50:
                    app_logger.info(f"Page {page_num + 1} has minimal text, using OCR")
                    text = self._ocr_page(pdf_path, page_num)

                page_texts.append({
                    "page_number": page_num + 1,
                    "text": text
                })
                full_text.append(text)

            # Extract metadata
            metadata = self.extract_metadata(doc)

            return {
                "full_text": "\n\n".join(full_text),
                "page_texts": page_texts,
                "page_count": page_count,
                "metadata": metadata
            }

        except Exception as e:
            app_logger.error(f"Error extracting PDF text: {str(e)}")
            raise

        finally:
            if doc is not None:
                try:
                    doc.close()
                except Exception:
                    pass
        
    
    def _ocr_page(self, pdf_path: str, page_num: int) -> str:
        """
        Perform OCR on a specific PDF page
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
        
        Returns:
            Extracted text from OCR
        """
        try:
            # Convert PDF page to image
            images = convert_from_path(
                pdf_path,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=300
            )
            
            if images:
                # Perform OCR on the image
                text = pytesseract.image_to_string(images[0])
                return text
            
            return ""
        
        except Exception as e:
            app_logger.error(f"OCR error on page {page_num}: {str(e)}")
            return ""
    
    def extract_metadata(self, doc: fitz.Document) -> Dict[str, any]:
        """
        Extract metadata from PDF document
        
        Args:
            doc: PyMuPDF document object
        
        Returns:
            Dictionary containing metadata
        """
        metadata = doc.metadata
        
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "mod_date": metadata.get("modDate", "")
        }
    
    def extract_toc(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Extract table of contents from PDF
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of TOC entries with level, title, and page
        """
        try:
            doc = fitz.open(pdf_path)
            toc = doc.get_toc()
            doc.close()
            
            formatted_toc = []
            for entry in toc:
                formatted_toc.append({
                    "level": entry[0],
                    "title": entry[1],
                    "page": entry[2]
                })
            
            return formatted_toc
        
        except Exception as e:
            app_logger.error(f"Error extracting TOC: {str(e)}")
            return []


# Global instance
pdf_service = PDFService()
