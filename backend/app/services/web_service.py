"""
Web scraping service for extracting content from URLs
Uses BeautifulSoup and html2text for clean text extraction
"""

import requests
from bs4 import BeautifulSoup
import html2text
from typing import Dict, Optional
from urllib.parse import urlparse
from app.utils.logger import app_logger
from app.config import settings


class WebService:
    """Service for scraping and extracting web content"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
    
    def scrape_url(self, url: str) -> Dict[str, any]:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
        
        Returns:
            Dictionary containing text, title, and metadata
        """
        try:
            app_logger.info(f"Scraping URL: {url}")
            
            # Make request
            response = requests.get(
                url,
                headers=self.headers,
                timeout=settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup)
            
            # Convert HTML to markdown
            markdown_content = self.html_converter.handle(str(content))
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            return {
                "url": url,
                "title": title,
                "content": markdown_content,
                "html_content": str(content),
                "content_length": len(markdown_content),
                "metadata": metadata
            }
        
        except requests.RequestException as e:
            app_logger.error(f"Error scraping URL {url}: {str(e)}")
            raise
        except Exception as e:
            app_logger.error(f"Unexpected error scraping URL {url}: {str(e)}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Untitled"
    
    def _extract_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Extract main content from page
        Removes scripts, styles, navigation, footer, etc.
        """
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            tag.decompose()
        
        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', class_='content') or
            soup.find('div', id='content') or
            soup.find('body')
        )
        
        return main_content if main_content else soup
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, any]:
        """Extract metadata from page"""
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc
        }
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata["description"] = meta_desc.get('content', '')
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata["keywords"] = meta_keywords.get('content', '')
        
        # Open Graph data
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata["og_title"] = og_title.get('content', '')
        
        og_description = soup.find('meta', property='og:description')
        if og_description:
            metadata["og_description"] = og_description.get('content', '')
        
        # Author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if author_tag:
            metadata["author"] = author_tag.get('content', '')
        
        return metadata


# Global instance
web_service = WebService()
