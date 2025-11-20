"""
Reranking engine for improved retrieval accuracy
Uses cross-encoder or scoring-based reranking
"""

from typing import List, Dict
from sentence_transformers import CrossEncoder
from app.utils.logger import app_logger
from app.config import settings
import numpy as np


class Reranker:
    """
    Reranking service to improve retrieval accuracy
    Uses cross-encoder for semantic relevance scoring
    """
    
    def __init__(self):
        """Initialize reranker with cross-encoder model"""
        self.model = None
        self.use_cross_encoder = True
        
        try:
            # Load cross-encoder model (lightweight)
            app_logger.info("Loading cross-encoder model for reranking...")
            self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            app_logger.info("Cross-encoder model loaded successfully")
        except Exception as e:
            app_logger.warning(f"Failed to load cross-encoder: {str(e)}")
            app_logger.info("Falling back to score-based reranking")
            self.use_cross_encoder = False
    
    def rerank(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Rerank chunks based on semantic relevance
        
        Args:
            query: User query
            chunks: List of retrieved chunks
            top_k: Number of top chunks to return
        
        Returns:
            Reranked list of chunks
        """
        if not chunks:
            return []
        
        try:
            if self.use_cross_encoder and self.model:
                return self._rerank_with_cross_encoder(query, chunks, top_k)
            else:
                return self._rerank_with_scores(query, chunks, top_k)
        
        except Exception as e:
            app_logger.error(f"Reranking error: {str(e)}")
            # Fallback: return original chunks
            return chunks[:top_k]
    
    def _rerank_with_cross_encoder(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """
        Rerank using cross-encoder model
        More accurate but slower than bi-encoder
        """
        try:
            # Prepare query-chunk pairs
            pairs = [[query, chunk['content']] for chunk in chunks]
            
            # Get relevance scores from cross-encoder
            scores = self.model.predict(pairs)
            
            # Add rerank scores to chunks
            for chunk, score in zip(chunks, scores):
                chunk['rerank_score'] = float(score)
            
            # Sort by rerank score (descending)
            reranked = sorted(
                chunks,
                key=lambda x: x['rerank_score'],
                reverse=True
            )
            
            app_logger.info(f"Cross-encoder reranking: {len(chunks)} → {top_k} chunks")
            
            return reranked[:top_k]
        
        except Exception as e:
            app_logger.error(f"Cross-encoder reranking failed: {str(e)}")
            return chunks[:top_k]
    
    def _rerank_with_scores(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """
        Rerank using existing relevance scores + heuristics
        Faster fallback method
        """
        try:
            # Apply heuristic scoring
            for chunk in chunks:
                base_score = chunk['relevance_score']
                
                # Bonus for query term matches (simple heuristic)
                query_terms = set(query.lower().split())
                content_terms = set(chunk['content'].lower().split())
                term_overlap = len(query_terms & content_terms)
                
                # Bonus for chunk position (earlier chunks often more relevant)
                position_bonus = 0.1 / (chunk['chunk_index'] + 1)
                
                # Bonus for having page numbers (structured content)
                page_bonus = 0.05 if chunk.get('page_number') else 0
                
                # Calculate enhanced score
                enhanced_score = (
                    base_score * 0.7 +
                    (term_overlap / max(len(query_terms), 1)) * 0.2 +
                    position_bonus +
                    page_bonus
                )
                
                chunk['rerank_score'] = enhanced_score
            
            # Sort by enhanced score
            reranked = sorted(
                chunks,
                key=lambda x: x['rerank_score'],
                reverse=True
            )
            
            app_logger.info(f"Score-based reranking: {len(chunks)} → {top_k} chunks")
            
            return reranked[:top_k]
        
        except Exception as e:
            app_logger.error(f"Score-based reranking failed: {str(e)}")
            return chunks[:top_k]
    
    def calculate_diversity(self, chunks: List[Dict]) -> float:
        """
        Calculate diversity score of retrieved chunks
        Higher diversity = chunks from different sources/sections
        
        Args:
            chunks: List of chunks
        
        Returns:
            Diversity score (0 to 1)
        """
        if not chunks:
            return 0.0
        
        # Count unique files
        unique_files = len(set(chunk['file_id'] for chunk in chunks))
        
        # Count unique pages (if available)
        unique_pages = len(set(
            chunk.get('page_number', -1)
            for chunk in chunks
            if chunk.get('page_number')
        ))
        
        # Diversity score based on distribution
        file_diversity = unique_files / len(chunks)
        page_diversity = unique_pages / len(chunks) if unique_pages > 0 else 0.5
        
        diversity_score = (file_diversity + page_diversity) / 2
        
        return diversity_score


# Global instance
reranker = Reranker()
