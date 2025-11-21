"""
Embedding generation service using Google Gemini API (FREE)
Converts text chunks into vector embeddings for semantic search
"""

import google.generativeai as genai
from typing import List
import numpy as np
from app.utils.logger import app_logger
from app.config import settings
import time


class EmbeddingService:
    """Service for generating text embeddings using Gemini"""
    
    def __init__(self):
        """Initialize the Gemini embedding model"""
        self.model_name = settings.EMBEDDING_MODEL
        self.embedding_dim = settings.EMBEDDING_DIMENSION

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for embedding generation")

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            app_logger.info(f"✅ Gemini embedding service initialized (model={self.model_name})")
        except Exception as e:
            app_logger.error(f"❌ Failed to initialize Gemini embedding service: {e}")
            raise
    
    def generate_embedding(self, text: str, retry_count: int = 3) -> np.ndarray:
        """
        Generate embedding for a single text using Gemini
        
        Args:
            text: Input text
            retry_count: Number of retries on failure
        
        Returns:
            Numpy array of embedding vector
        """
        for attempt in range(retry_count):
            try:
                app_logger.debug(f"Attempting Gemini embedding (attempt {attempt + 1}/{retry_count})")
                result = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                embedding = np.array(result['embedding'], dtype=np.float32)
                app_logger.debug(f"✅ Gemini embedding generated successfully")
                return embedding
            except Exception as e:
                msg = str(e)
                error_code = None
                if hasattr(e, 'status_code'):
                    error_code = e.status_code
                
                app_logger.warning(f"Gemini embedding attempt {attempt + 1}/{retry_count} failed: {msg[:200]}")
                
                is_quota_error = 'quota' in msg.lower() or '429' in msg or error_code == 429
                is_final_attempt = attempt == retry_count - 1
                
                if is_final_attempt:
                    if is_quota_error:
                        app_logger.error(f"❌ Gemini quota exceeded after {retry_count} attempts.")
                        app_logger.error(f"💡 TIP: Check your Gemini API quota at https://ai.dev/usage?tab=rate-limit")
                    else:
                        app_logger.error(f"❌ All {retry_count} Gemini embedding attempts failed.")
                    # Return zero vector as fallback
                    return np.zeros(self.embedding_dim, dtype=np.float32)
                else:
                    # Exponential backoff for retries
                    wait_time = 2 ** attempt if not is_quota_error else 5
                    app_logger.info(f"Retrying Gemini embedding in {wait_time}s...")
                    time.sleep(wait_time)
        
        # Fallback: return zero vector
        app_logger.error(f"❌ All embedding attempts exhausted. Returning zero vector.")
        return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing (Gemini free tier: 100/min)
        
        Returns:
            List of embedding vectors
        """
        try:
            app_logger.info(f"Generating embeddings for {len(texts)} texts")

            embeddings = []
            # Process in batches to respect rate limits
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                for text in batch:
                    embedding = self.generate_embedding(text)
                    embeddings.append(embedding)

                # Rate limiting: wait 1 second between batches
                if i + batch_size < len(texts):
                    app_logger.info(f"Processed {i + len(batch)}/{len(texts)} embeddings...")
                    time.sleep(1)

            app_logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            app_logger.error(f"❌ Error generating batch embeddings: {str(e)}")
            raise
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query (optimized for search)
        
        Args:
            query: Search query text
        
        Returns:
            Numpy array of embedding vector
        """
        try:
            # Use query-specific task type
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )

            embedding = np.array(result['embedding'], dtype=np.float32)
            return embedding

        except Exception as e:
            app_logger.error(f"❌ Error generating query embedding: {str(e)}")
            # Fallback to document embedding
            return self.generate_embedding(query)
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score (0 to 1)
        """
        try:
            # Normalize vectors
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Compute cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            app_logger.error(f"❌ Error computing similarity: {str(e)}")
            return 0.0


# Global instance
embedding_service = EmbeddingService()
