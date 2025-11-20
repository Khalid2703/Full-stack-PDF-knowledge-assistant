"""
Metadata extraction service for Smart Sections View
Extracts TOC, entities, summaries, and other metadata
"""

import re
from typing import List, Dict, Optional
from collections import Counter
from app.utils.logger import app_logger


class MetadataService:
    """Service for extracting enhanced metadata from documents"""
    
    def extract_entities(self, text: str, top_n: int = 20) -> List[str]:
        """
        Extract key entities (capitalized words/phrases)
        Simple NER without external libraries
        
        Args:
            text: Input text
            top_n: Number of top entities to return
        
        Returns:
            List of entity strings
        """
        try:
            # Find capitalized words (potential entities)
            # Pattern: Words starting with capital letter, 2+ chars
            pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            entities = re.findall(pattern, text)
            
            # Filter out common words
            stop_words = {'The', 'This', 'That', 'These', 'Those', 'A', 'An', 'In', 'On', 'At', 'To', 'For'}
            entities = [e for e in entities if e not in stop_words]
            
            # Count frequencies
            entity_counts = Counter(entities)
            
            # Return top entities
            top_entities = [entity for entity, count in entity_counts.most_common(top_n)]
            
            return top_entities
        
        except Exception as e:
            app_logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """
        Generate simple extractive summary
        Takes first and most relevant sentences
        
        Args:
            text: Input text
            max_length: Maximum summary length
        
        Returns:
            Summary string
        """
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            if not sentences:
                return ""
            
            # Take first 3 sentences as summary
            summary_sentences = sentences[:3]
            summary = '. '.join(summary_sentences) + '.'
            
            # Truncate if too long
            if len(summary) > max_length:
                summary = summary[:max_length] + '...'
            
            return summary
        
        except Exception as e:
            app_logger.error(f"Error generating summary: {str(e)}")
            return ""
    
    def extract_sections(self, text: str) -> List[Dict[str, any]]:
        """
        Extract sections from text based on headings
        
        Args:
            text: Input text
        
        Returns:
            List of section dictionaries
        """
        try:
            sections = []
            
            # Pattern for markdown-style headings
            heading_pattern = r'^(#{1,6})\s+(.+)$'
            
            lines = text.split('\n')
            current_section = None
            
            for i, line in enumerate(lines):
                match = re.match(heading_pattern, line)
                if match:
                    level = len(match.group(1))
                    title = match.group(2).strip()
                    
                    if current_section:
                        sections.append(current_section)
                    
                    current_section = {
                        'level': level,
                        'title': title,
                        'line_number': i + 1,
                        'content': []
                    }
                elif current_section:
                    current_section['content'].append(line)
            
            # Add last section
            if current_section:
                sections.append(current_section)
            
            return sections
        
        except Exception as e:
            app_logger.error(f"Error extracting sections: {str(e)}")
            return []
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def analyze_document(self, text: str, toc: Optional[List[Dict]] = None) -> Dict[str, any]:
        """
        Perform comprehensive document analysis
        
        Args:
            text: Full document text
            toc: Optional table of contents
        
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                'word_count': self.count_words(text),
                'character_count': len(text),
                'entities': self.extract_entities(text),
                'summary': self.generate_summary(text),
                'sections': self.extract_sections(text) if not toc else [],
                'toc': toc if toc else []
            }
            
            return analysis
        
        except Exception as e:
            app_logger.error(f"Error analyzing document: {str(e)}")
            return {}


# Global instance
metadata_service = MetadataService()
