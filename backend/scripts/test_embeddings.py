"""
Test script for embedding service
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.embedding_service import embedding_service
from app.utils.logger import app_logger


def test_embeddings():
    """Test embedding generation"""
    try:
        # Test single embedding
        text = "This is a test document about artificial intelligence."
        embedding = embedding_service.generate_embedding(text)
        
        app_logger.info(f"✅ Single embedding generated")
        app_logger.info(f"   Dimension: {len(embedding)}")
        app_logger.info(f"   First 5 values: {embedding[:5]}")
        
        # Test batch embeddings
        texts = [
            "Machine learning is a subset of AI",
            "Natural language processing enables computers to understand text",
            "Deep learning uses neural networks"
        ]
        
        embeddings = embedding_service.generate_embeddings_batch(texts)
        app_logger.info(f"✅ Batch embeddings generated: {len(embeddings)} embeddings")
        
        # Test similarity
        similarity = embedding_service.compute_similarity(embeddings[0], embeddings[1])
        app_logger.info(f"✅ Similarity between text 1 and 2: {similarity:.4f}")
        
    except Exception as e:
        app_logger.error(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    test_embeddings()
