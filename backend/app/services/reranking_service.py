"""
Reranking service for improving RAG retrieval quality
Uses Gemini API for semantic similarity scoring
"""

import google.generativeai as genai
from typing import List, Dict
import numpy as np
from app.utils.logger import app_logger
from app.config import settings


class RerankingService:
    """Service for reranking retrieved documents using Gemini"""
    
    def __init__(self):
        """Initialize reranking service"""
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required for reranking")
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model_name = "models/embedding-001"
            self.enabled = True
            app_logger.info("✅ Gemini-based reranking service initialized")
            
        except Exception as e:
            app_logger.warning(f"⚠️ Reranking service disabled: {str(e)}")
            self.enabled = False
    
    def _compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using Gemini"""
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_query"
            )
            return np.array(result['embedding'], dtype=np.float32)
        except Exception as e:
            app_logger.warning(f"Embedding generation failed: {e}")
            return np.zeros(768, dtype=np.float32)
    
    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = None
    ) -> List[Dict]:
        """
        Rerank documents based on semantic similarity to query
        
        Args:
            query: Search query
            documents: List of document dicts with 'content' field
            top_k: Number of top documents to return (None = return all)
        
        Returns:
            Reranked list of documents with updated scores
        """
        if not self.enabled or not documents:
            return documents
        
        try:
            # Get query embedding once
            query_embedding = self._get_embedding(query)
            
            # Calculate similarity for each document
            for doc in documents:
                try:
                    doc_embedding = self._get_embedding(doc['content'][:500])  # Use first 500 chars
                    similarity = self._compute_similarity(query_embedding, doc_embedding)
                    
                    doc['rerank_score'] = float(similarity)
                    # Combine with original relevance score if available
                    original_score = doc.get('relevance_score', 0.5)
                    doc['final_score'] = (original_score + similarity) / 2
                    
                except Exception as e:
                    app_logger.warning(f"Failed to rerank document: {e}")
                    doc['rerank_score'] = doc.get('relevance_score', 0.5)
                    doc['final_score'] = doc.get('relevance_score', 0.5)
            
            # Sort by final score
            reranked = sorted(documents, key=lambda x: x.get('final_score', 0), reverse=True)
            
            # Return top k if specified
            if top_k:
                reranked = reranked[:top_k]
            
            app_logger.info(f"✅ Reranked {len(documents)} documents using Gemini")
            return reranked
            
        except Exception as e:
            app_logger.error(f"❌ Reranking error: {str(e)}")
            return documents
    
    def score_answer_quality(
        self,
        query: str,
        answer: str,
        sources: List[str]
    ) -> Dict[str, float]:
        """
        Score the quality of a generated answer using Gemini embeddings
        
        Args:
            query: Original query
            answer: Generated answer
            sources: Source documents used
        
        Returns:
            Dict with quality scores
        """
        scores = {
            'relevance': 0.0,
            'groundedness': 0.0,
            'completeness': 0.0,
            'overall': 0.0
        }
        
        if not self.enabled:
            return scores
        
        try:
            # 1. Relevance: How well does answer address query
            query_emb = self._get_embedding(query)
            answer_emb = self._get_embedding(answer)
            scores['relevance'] = self._compute_similarity(query_emb, answer_emb)
            
            # 2. Groundedness: How well is answer supported by sources
            if sources:
                groundedness_scores = []
                for source in sources[:3]:  # Check top 3 sources
                    source_emb = self._get_embedding(source[:500])
                    similarity = self._compute_similarity(answer_emb, source_emb)
                    groundedness_scores.append(similarity)
                scores['groundedness'] = float(np.mean(groundedness_scores))
            
            # 3. Completeness: Length and detail (heuristic)
            answer_length = len(answer.split())
            if answer_length < 20:
                scores['completeness'] = 0.3
            elif answer_length < 50:
                scores['completeness'] = 0.6
            else:
                scores['completeness'] = 0.9
            
            # 4. Overall score
            scores['overall'] = (
                scores['relevance'] * 0.4 +
                scores['groundedness'] * 0.4 +
                scores['completeness'] * 0.2
            )
            
            app_logger.debug(f"Answer quality scores: {scores}")
            return scores
            
        except Exception as e:
            app_logger.error(f"❌ Answer scoring error: {str(e)}")
            return scores


# Global instance
reranking_service = RerankingService()
