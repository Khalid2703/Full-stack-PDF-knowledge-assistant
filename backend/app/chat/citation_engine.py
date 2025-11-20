"""
Citation engine for source-grounded answers
Generates accurate citations with chunk-level attribution
"""

from typing import List, Dict, Optional
import re
from app.utils.logger import app_logger


class CitationEngine:
    """
    Citation management and verification system
    Ensures all claims are properly attributed to source chunks
    """
    
    def __init__(self):
        """Initialize citation engine"""
        self.citation_pattern = r'\[Source (\d+)\]'
    
    def add_citations(
        self,
        answer: str,
        chunks: List[Dict],
        auto_cite: bool = True
    ) -> str:
        """
        Add or enhance citations in answer text
        
        Args:
            answer: Generated answer
            chunks: Source chunks
            auto_cite: Automatically add citations if missing
        
        Returns:
            Answer with proper citations
        """
        if not chunks:
            return answer
        
        # Check if answer already has citations
        existing_citations = re.findall(self.citation_pattern, answer)
        
        if existing_citations:
            app_logger.info(f"Answer already has {len(existing_citations)} citations")
            return answer
        
        if auto_cite:
            # Auto-generate citations based on content matching
            return self._auto_generate_citations(answer, chunks)
        
        return answer
    
    def _auto_generate_citations(self, answer: str, chunks: List[Dict]) -> str:
        """
        Automatically add citations by matching answer content to chunks
        """
        # Split answer into sentences
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        cited_sentences = []
        
        for sentence in sentences:
            best_match_idx = None
            best_match_score = 0
            
            # Find best matching chunk for this sentence
            for idx, chunk in enumerate(chunks):
                score = self._calculate_overlap(sentence, chunk['content'])
                if score > best_match_score:
                    best_match_score = score
                    best_match_idx = idx
            
            # Add citation if good match found
            if best_match_idx is not None and best_match_score > 0.3:
                cited_sentence = f"{sentence} [Source {best_match_idx + 1}]"
            else:
                cited_sentence = sentence
            
            cited_sentences.append(cited_sentence)
        
        return '. '.join(cited_sentences) + '.'
    
    def _calculate_overlap(self, text1: str, text2: str) -> float:
        """
        Calculate word overlap between two texts
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Overlap score (0 to 1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1:
            return 0.0
        
        overlap = len(words1 & words2)
        return overlap / len(words1)
    
    def extract_citations(self, answer: str) -> List[int]:
        """
        Extract citation numbers from answer
        
        Args:
            answer: Answer text with citations
        
        Returns:
            List of cited source numbers
        """
        citations = re.findall(self.citation_pattern, answer)
        return [int(c) for c in citations]
    
    def verify_citations(
        self,
        answer: str,
        chunks: List[Dict]
    ) -> Dict[str, any]:
        """
        Verify that all citations are valid and map to actual chunks
        
        Args:
            answer: Answer with citations
            chunks: Source chunks
        
        Returns:
            Verification report
        """
        citation_numbers = self.extract_citations(answer)
        
        report = {
            "total_citations": len(citation_numbers),
            "valid_citations": 0,
            "invalid_citations": [],
            "citation_coverage": 0.0,
            "chunks_cited": set()
        }
        
        max_source_num = len(chunks)
        
        for num in citation_numbers:
            if 1 <= num <= max_source_num:
                report["valid_citations"] += 1
                report["chunks_cited"].add(num - 1)  # 0-indexed
            else:
                report["invalid_citations"].append(num)
        
        # Calculate coverage
        if chunks:
            report["citation_coverage"] = len(report["chunks_cited"]) / len(chunks)
        
        report["chunks_cited"] = list(report["chunks_cited"])
        
        return report
    
    def format_citations(
        self,
        chunks: List[Dict],
        style: str = "numbered"
    ) -> str:
        """
        Format chunk citations for display
        
        Args:
            chunks: Source chunks
            style: Citation style (numbered, named, apa)
        
        Returns:
            Formatted citation list
        """
        if not chunks:
            return ""
        
        citations = []
        
        if style == "numbered":
            for i, chunk in enumerate(chunks):
                citation = f"[{i+1}] {chunk['filename']}"
                if chunk.get('page_number'):
                    citation += f", Page {chunk['page_number']}"
                citations.append(citation)
        
        elif style == "named":
            for chunk in chunks:
                citation = f"• {chunk['filename']}"
                if chunk.get('page_number'):
                    citation += f" (Page {chunk['page_number']})"
                citations.append(citation)
        
        elif style == "apa":
            for chunk in chunks:
                title = chunk.get('filename', 'Unknown')
                page = chunk.get('page_number', 'n.p.')
                citation = f"{title} (p. {page})"
                citations.append(citation)
        
        return "\n".join(citations)
    
    def generate_citation_metadata(
        self,
        answer: str,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        Generate detailed metadata for each citation
        
        Args:
            answer: Answer with citations
            chunks: Source chunks
        
        Returns:
            List of citation metadata dictionaries
        """
        citation_numbers = self.extract_citations(answer)
        
        metadata = []
        
        for num in citation_numbers:
            if 1 <= num <= len(chunks):
                chunk = chunks[num - 1]
                meta = {
                    "citation_number": num,
                    "file_id": chunk["file_id"],
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"],
                    "page_number": chunk.get("page_number"),
                    "relevance_score": chunk.get("relevance_score", 0),
                    "rerank_score": chunk.get("rerank_score"),
                    "content_preview": chunk["content"][:200] + "...",
                    "url": chunk.get("url")  # If from web source
                }
                metadata.append(meta)
        
        return metadata


# Global instance
citation_engine = CitationEngine()
