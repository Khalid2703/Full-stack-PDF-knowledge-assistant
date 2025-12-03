"""
Embedding generation service with dual provider support
Primary: OpenAI (text-embedding-3-small)
Fallback: Google Gemini (embedding-001)
"""

import google.generativeai as genai
from openai import OpenAI
from typing import List
import numpy as np
from app.utils.logger import app_logger
from app.config import settings
import time


class EmbeddingService:
    """Service for generating text embeddings with dual provider support"""
    
    def __init__(self):
        """Initialize embedding services (OpenAI primary, Gemini fallback)"""
        self.openai_client = None
        self.gemini_configured = False
        self.use_openai = False
        
        # Determine which provider to use
        provider = getattr(settings, 'EMBEDDING_PROVIDER', 'openai').lower()
        
        # Try OpenAI first (if provider is openai or auto)
        if provider in ['openai', 'auto'] and settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                # Test the connection
                self.openai_client.models.list()
                
                # Get model and dimension from settings or use defaults
                self.openai_model = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
                self.embedding_dim = getattr(settings, 'OPENAI_EMBEDDING_DIMENSION', 1536)
                
                self.use_openai = True
                app_logger.info(f"✅ OpenAI embedding service initialized (PRIMARY)")
                app_logger.info(f"   Model: {self.openai_model}")
                app_logger.info(f"   Dimension: {self.embedding_dim}")
            except Exception as e:
                app_logger.warning(f"⚠️ OpenAI embedding initialization failed: {str(e)}")
                self.openai_client = None
        
        # Configure Gemini as fallback (or primary if provider is gemini)
        if not self.use_openai or provider == 'gemini':
            try:
                if not settings.GEMINI_API_KEY:
                    if not self.use_openai:
                        raise ValueError("No embedding provider configured. Set OPENAI_API_KEY or GEMINI_API_KEY")
                    # OpenAI is available, just log warning about Gemini
                    app_logger.warning("⚠️ Gemini fallback not available (no API key)")
                else:
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    self.gemini_model = settings.EMBEDDING_MODEL
                    self.gemini_configured = True
                    
                    if provider == 'gemini' or not self.use_openai:
                        # Gemini is primary
                        self.embedding_dim = settings.EMBEDDING_DIMENSION
                        self.use_openai = False
                        app_logger.info(f"✅ Gemini embedding service initialized (PRIMARY)")
                        app_logger.info(f"   Model: {self.gemini_model}")
                        app_logger.info(f"   Dimension: {self.embedding_dim}")
                    else:
                        # Gemini is fallback
                        app_logger.info("✅ Gemini embedding fallback configured")
                        
            except Exception as e:
                if not self.use_openai:
                    app_logger.error(f"❌ Error initializing embedding services: {str(e)}")
                    raise
                app_logger.warning(f"⚠️ Gemini fallback not available: {str(e)}")
    
    def generate_embedding(self, text: str, retry_count: int = 3) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            retry_count: Number of retries on failure
        
        Returns:
            Numpy array of embedding vector
        """
        # Try OpenAI first
        if self.use_openai and self.openai_client:
            for attempt in range(retry_count):
                try:
                    embedding = self._generate_openai_embedding(text)
                    if embedding is not None:
                        return embedding
                except Exception as e:
                    app_logger.warning(f"OpenAI embedding attempt {attempt + 1}/{retry_count} failed: {str(e)}")
                    if attempt < retry_count - 1:
                        time.sleep(1)
                    elif self.gemini_configured:
                        app_logger.info("Falling back to Gemini...")
                        break
        
        # Fallback to Gemini
        if self.gemini_configured:
            return self._generate_gemini_embedding(text, retry_count)
        
        # Return zero vector as last resort
        app_logger.error("❌ All embedding providers failed. Returning zero vector.")
        return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def _generate_openai_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI"""
        response = self.openai_client.embeddings.create(
            model=self.openai_model,
            input=text,
            encoding_format="float"
        )
        
        embedding = np.array(response.data[0].embedding, dtype=np.float32)
        app_logger.debug(f"✅ OpenAI embedding generated (dim={len(embedding)})")
        return embedding
    
    def _generate_gemini_embedding(self, text: str, retry_count: int = 3) -> np.ndarray:
        """Generate embedding using Gemini with retries"""
        for attempt in range(retry_count):
            try:
                result = genai.embed_content(
                    model=self.gemini_model,
                    content=text,
                    task_type="retrieval_document"
                )
                embedding = np.array(result['embedding'], dtype=np.float32)
                app_logger.debug(f"✅ Gemini embedding generated (dim={len(embedding)})")
                return embedding
                
            except Exception as e:
                msg = str(e)
                error_code = getattr(e, 'status_code', None)
                
                app_logger.warning(f"Gemini embedding attempt {attempt + 1}/{retry_count} failed: {msg[:200]}")
                
                is_quota_error = 'quota' in msg.lower() or '429' in msg or error_code == 429
                is_final_attempt = attempt == retry_count - 1
                
                if is_final_attempt:
                    if is_quota_error:
                        app_logger.error(f"❌ Gemini quota exceeded after {retry_count} attempts.")
                        app_logger.error(f"💡 TIP: Check your Gemini API quota at https://ai.dev/usage?tab=rate-limit")
                    else:
                        app_logger.error(f"❌ All {retry_count} Gemini embedding attempts failed.")
                    return np.zeros(self.embedding_dim, dtype=np.float32)
                else:
                    wait_time = 5 if is_quota_error else (2 ** attempt)
                    app_logger.info(f"Retrying Gemini embedding in {wait_time}s...")
                    time.sleep(wait_time)
        
        return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
        
        Returns:
            List of embedding vectors
        """
        try:
            app_logger.info(f"Generating embeddings for {len(texts)} texts")
            
            embeddings = []
            
            if self.use_openai and self.openai_client:
                # OpenAI supports larger batches (up to 2048)
                batch_size = min(batch_size, 100)
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    
                    try:
                        # Batch request to OpenAI
                        response = self.openai_client.embeddings.create(
                            model=self.openai_model,
                            input=batch,
                            encoding_format="float"
                        )
                        
                        batch_embeddings = [
                            np.array(item.embedding, dtype=np.float32)
                            for item in response.data
                        ]
                        embeddings.extend(batch_embeddings)
                        
                        app_logger.info(f"Processed {len(embeddings)}/{len(texts)} embeddings (OpenAI)...")
                        
                    except Exception as e:
                        app_logger.warning(f"OpenAI batch failed: {str(e)}, falling back to individual processing")
                        # Fallback to individual processing for this batch
                        for text in batch:
                            embedding = self.generate_embedding(text)
                            embeddings.append(embedding)
            else:
                # Gemini: process one by one with rate limiting
                batch_size = min(batch_size, 100)  # Respect Gemini's 100/min limit
                
                for i, text in enumerate(texts):
                    embedding = self.generate_embedding(text)
                    embeddings.append(embedding)
                    
                    # Rate limiting: wait 1 second after each batch
                    if (i + 1) % batch_size == 0 and (i + 1) < len(texts):
                        app_logger.info(f"Processed {i + 1}/{len(texts)} embeddings...")
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
            if self.use_openai and self.openai_client:
                # OpenAI: same model for queries
                return self._generate_openai_embedding(query)
            elif self.gemini_configured:
                # Gemini: use query-specific task type
                result = genai.embed_content(
                    model=self.gemini_model,
                    content=query,
                    task_type="retrieval_query"
                )
                return np.array(result['embedding'], dtype=np.float32)
            else:
                return np.zeros(self.embedding_dim, dtype=np.float32)
                
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
