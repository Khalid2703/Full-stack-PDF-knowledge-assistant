"""
Reranking engine for improved retrieval accuracy
Uses Gemini embeddings for semantic relevance scoring
"""

from typing import List, Dict
import google.generativeai as genai
import numpy as np
from app.utils.logger import app_logger
from app.config import settings


class Reranker:
    """
    Reranking service to improve retrieval accuracy
    Uses Gemini embeddings for semantic relevance scoring
    """
    
    def __init__(self):
        """Initialize reranker with Gemini API"""
        self.enabled = False
        self.model_name = "models/embedding-001"
        
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY required")
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.enabled = True
            app_logger.info("✅ Gemini-based reranker initialized")
            
        except Exception as e:
            app_logger.warning(f"⚠️ Reranker disabled: {str(e)}")
            app_logger.info("Using score-based reranking as fallback")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using Gemini"""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text[:500],  # Limit to 500 chars for efficiency
                task_type="retrieval_query"
            )
            return np.array(result['embedding'], dtype=np.float32)
        except Exception as e:
            app_logger.warning(f"Embedding generation failed: {e}")
            return np.zeros(768, dtype=np.float32)
    
    def _compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
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
            if self.enabled:
                return self._rerank_with_gemini(query, chunks, top_k)
            else:
                return self._rerank_with_scores(query, chunks, top_k)
        
        except Exception as e:
            app_logger.error(f"Reranking error: {str(e)}")
            # Fallback: return original chunks
            return chunks[:top_k]
    
    def _rerank_with_gemini(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """
        Rerank using Gemini embeddings
        More accurate semantic matching
        """
        try:
            # Get query embedding once
            query_embedding = self._get_embedding(query)
            
            # Calculate similarity for each chunk
            for chunk in chunks:
                chunk_embedding = self._get_embedding(chunk['content'])
                similarity = self._compute_similarity(query_embedding, chunk_embedding)
                chunk['rerank_score'] = float(similarity)
            
            # Sort by rerank score (descending)
            reranked = sorted(
                chunks,
                key=lambda x: x['rerank_score'],
                reverse=True
            )
            
            app_logger.info(f"✅ Gemini reranking: {len(chunks)} → {top_k} chunks")
            
            return reranked[:top_k]
        
        except Exception as e:
            app_logger.error(f"Gemini reranking failed: {str(e)}")
            return self._rerank_with_scores(query, chunks, top_k)
    
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
                base_score = chunk.get('relevance_score', 0.5)
                
                # Bonus for query term matches (simple heuristic)
                query_terms = set(query.lower().split())
                content_terms = set(chunk['content'].lower().split())
                term_overlap = len(query_terms & content_terms)
                
                # Bonus for chunk position (earlier chunks often more relevant)
                position_bonus = 0.1 / (chunk.get('chunk_index', 0) + 1)
                
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
        unique_files = len(set(chunk.get('file_id', 'unknown') for chunk in chunks))
        
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
