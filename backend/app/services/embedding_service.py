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


def _init_local_sentence_model(model_name: str = 'all-MiniLM-L6-v2'):
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise ImportError(
            "Local sentence-transformers fallback requested but package is not installed. "
            "Install with: pip install sentence-transformers"
        ) from e

    model = SentenceTransformer(model_name)
    return model


class EmbeddingService:
    """Service for generating text embeddings using Gemini"""
    
    def __init__(self):
        """Initialize the Gemini embedding model"""
        # Decide which backend to use: Gemini (if API key present) or local sentence-transformers
        self.model_name = settings.EMBEDDING_MODEL
        self.embedding_dim = settings.EMBEDDING_DIMENSION
        self.backend = None
        self.local_model = None

        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.backend = 'gemini'
                app_logger.info(f"✅ Gemini embedding service initialized (model={self.model_name})")
            except Exception as e:
                app_logger.warning(f"⚠️ Gemini init failed, falling back to local model: {e}")
                try:
                    self.local_model = _init_local_sentence_model()
                    self.embedding_dim = self.local_model.get_sentence_embedding_dimension()
                    self.backend = 'local'
                    app_logger.info(f"✅ Local sentence-transformers fallback initialized (dim={self.embedding_dim})")
                except Exception as ie:
                    app_logger.error(f"❌ Failed to initialize any embedding backend: {ie}")
                    raise
        else:
            # No Gemini key: try local model
            try:
                self.local_model = _init_local_sentence_model()
                self.embedding_dim = self.local_model.get_sentence_embedding_dimension()
                self.backend = 'local'
                app_logger.info(f"✅ Local sentence-transformers initialized (dim={self.embedding_dim})")
            except Exception as e:
                app_logger.error(f"❌ No embedding backend available: {e}")
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
        # If backend is local, use sentence-transformers encode (fast)
        if self.backend == 'local' and self.local_model is not None:
            try:
                emb = self.local_model.encode(text, convert_to_numpy=True)
                return np.array(emb, dtype=np.float32)
            except Exception as e:
                app_logger.error(f"❌ Local embedding failed: {e}")
                return np.zeros(self.embedding_dim, dtype=np.float32)

        # Prioritize Gemini - attempt multiple times before falling back
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
                
                # Only switch to local on persistent quota errors or after all retries
                is_quota_error = 'quota' in msg.lower() or '429' in msg or error_code == 429
                is_final_attempt = attempt == retry_count - 1
                
                if is_quota_error and is_final_attempt:
                    app_logger.error(f"❌ Gemini quota exceeded after {retry_count} attempts. Switching to local fallback.")
                    app_logger.error(f"⚠️ NOTE: Local embeddings have different dimensions. Index will be automatically reindexed.")
                    app_logger.error(f"💡 TIP: Check your Gemini API quota at https://ai.dev/usage?tab=rate-limit")
                    
                    try:
                        if self.local_model is None:
                            self.local_model = _init_local_sentence_model()
                            new_dim = self.local_model.get_sentence_embedding_dimension()
                            if new_dim != self.embedding_dim:
                                app_logger.warning(f"⚠️ Embedding dimension changed: {self.embedding_dim} → {new_dim}. FAISS index will be reindexed.")
                            self.embedding_dim = new_dim
                        self.backend = 'local'
                        emb = self.local_model.encode(text, convert_to_numpy=True)
                        app_logger.info(f"✅ Using local sentence-transformers embeddings (dim={self.embedding_dim})")
                        return np.array(emb, dtype=np.float32)
                    except Exception as ie:
                        app_logger.error(f"❌ Local embedding fallback also failed: {ie}")
                        return np.zeros(self.embedding_dim, dtype=np.float32)
                elif not is_quota_error and not is_final_attempt:
                    # For non-quota errors, retry after a delay
                    wait_time = 2 ** attempt  # Exponential backoff
                    app_logger.info(f"Retrying Gemini embedding in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    # For quota errors on non-final attempts, wait longer
                    wait_time = 5
                    app_logger.info(f"Quota error detected. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        # If we get here, all retries failed but it wasn't a quota error
        app_logger.error(f"❌ All {retry_count} Gemini embedding attempts failed. Falling back to local.")
        try:
            if self.local_model is None:
                self.local_model = _init_local_sentence_model()
                new_dim = self.local_model.get_sentence_embedding_dimension()
                if new_dim != self.embedding_dim:
                    app_logger.warning(f"⚠️ Embedding dimension changed: {self.embedding_dim} → {new_dim}")
                self.embedding_dim = new_dim
            self.backend = 'local'
            emb = self.local_model.encode(text, convert_to_numpy=True)
            return np.array(emb, dtype=np.float32)
        except Exception as ie:
            app_logger.error(f"❌ Local embedding fallback failed: {ie}")
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

            # If local backend available we can batch-encode efficiently
            if self.backend == 'local' and self.local_model is not None:
                try:
                    embs = self.local_model.encode(texts, convert_to_numpy=True, batch_size=batch_size)
                    # Ensure dtype and shape
                    return [np.array(e, dtype=np.float32) for e in embs]
                except Exception as e:
                    app_logger.warning(f"Local batch encoding failed, falling back to per-item: {e}")

            embeddings = []
            # Process in batches to respect rate limits for remote provider
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
        # If using local backend, use it for query embeddings as well
        if self.backend == 'local' and self.local_model is not None:
            try:
                emb = self.local_model.encode(query, convert_to_numpy=True)
                return np.array(emb, dtype=np.float32)
            except Exception as e:
                app_logger.warning(f"Local query embedding failed, falling back: {e}")

        try:
            # Use query-specific task type on Gemini
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )

            embedding = np.array(result['embedding'], dtype=np.float32)
            return embedding

        except Exception as e:
            app_logger.error(f"❌ Error generating query embedding: {str(e)}")
            # Fallback to document embedding which will try local if available
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
