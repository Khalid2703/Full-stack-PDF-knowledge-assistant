"""
Reranking service for improving RAG retrieval quality
Uses cross-encoder and custom scoring
"""

from sentence_transformers import CrossEncoder
from typing import List, Dict
import numpy as np
from app.utils.logger import app_logger
from app.config import settings


class RerankingService:
    """Service for reranking retrieved documents"""
    
    def __init__(self):
        """Initialize reranking model"""
        try:
            # Use lightweight cross-encoder for reranking
            self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            app_logger.info("✅ Reranking service initialized")
            
        except Exception as e:
            app_logger.error(f"❌ Error initializing reranking service: {str(e)}")
            self.model = None
    
    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = None
    ) -> List[Dict]:
        """
        Rerank documents based on relevance to query
        
        Args:
            query: Search query
            documents: List of document dicts with 'content' field
            top_k: Number of top documents to return (None = return all)
        
        Returns:
            Reranked list of documents with updated scores
        """
        if not self.model or not documents:
            return documents
        
        try:
            # Prepare query-document pairs
            pairs = [[query, doc['content']] for doc in documents]
            
            # Get cross-encoder scores
            scores = self.model.predict(pairs)
            
            # Add rerank scores to documents
            for doc, score in zip(documents, scores):
                doc['rerank_score'] = float(score)
                # Combine with original relevance score
                doc['final_score'] = (doc.get('relevance_score', 0.5) + float(score)) / 2
            
            # Sort by final score
            reranked = sorted(documents, key=lambda x: x['final_score'], reverse=True)
            
            # Return top k if specified
            if top_k:
                reranked = reranked[:top_k]
            
            app_logger.info(f"✅ Reranked {len(documents)} documents")
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
        Score the quality of a generated answer
        
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
        
        if not self.model:
            return scores
        
        try:
            # 1. Relevance: How well does answer address query
            relevance_score = self.model.predict([[query, answer]])[0]
            scores['relevance'] = float(relevance_score)
            
            # 2. Groundedness: How well is answer supported by sources
            if sources:
                groundedness_scores = []
                for source in sources[:3]:  # Check top 3 sources
                    score = self.model.predict([[answer, source]])[0]
                    groundedness_scores.append(float(score))
                scores['groundedness'] = np.mean(groundedness_scores)
            
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
            
            return scores
            
        except Exception as e:
            app_logger.error(f"❌ Answer scoring error: {str(e)}")
            return scores


# Global instance
reranking_service = RerankingService()
