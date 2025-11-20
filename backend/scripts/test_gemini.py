"""
Test script for Google Gemini API integration
Tests embeddings and chat generation
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.utils.logger import app_logger


def test_gemini_embeddings():
    """Test Gemini embedding generation"""
    app_logger.info("=" * 60)
    app_logger.info("TESTING GEMINI EMBEDDINGS")
    app_logger.info("=" * 60)
    
    try:
        # Test single embedding
        text = "This is a test document about artificial intelligence and machine learning."
        app_logger.info(f"\n📝 Text: {text}")
        
        embedding = embedding_service.generate_embedding(text)
        
        app_logger.info(f"✅ Embedding generated successfully!")
        app_logger.info(f"   Dimension: {len(embedding)}")
        app_logger.info(f"   First 5 values: {embedding[:5]}")
        app_logger.info(f"   Type: {type(embedding)}")
        
        # Test query embedding
        query = "What is AI?"
        query_embedding = embedding_service.generate_query_embedding(query)
        
        app_logger.info(f"\n✅ Query embedding generated!")
        app_logger.info(f"   Query: {query}")
        app_logger.info(f"   Dimension: {len(query_embedding)}")
        
        # Test similarity
        similarity = embedding_service.compute_similarity(embedding, query_embedding)
        app_logger.info(f"\n✅ Similarity computed: {similarity:.4f}")
        
        return True
        
    except Exception as e:
        app_logger.error(f"❌ Embedding test failed: {str(e)}")
        return False


def test_gemini_chat():
    """Test Gemini chat generation"""
    app_logger.info("\n" + "=" * 60)
    app_logger.info("TESTING GEMINI CHAT GENERATION")
    app_logger.info("=" * 60)
    
    try:
        # Test simple generation
        prompt = "What is machine learning? Explain in 2-3 sentences."
        app_logger.info(f"\n📝 Prompt: {prompt}")
        
        response = llm_service.generate_response(prompt)
        
        app_logger.info(f"\n✅ Response generated successfully!")
        app_logger.info(f"   Response: {response}")
        app_logger.info(f"   Length: {len(response)} characters")
        
        # Test with context
        context = "Machine learning is a subset of AI that enables computers to learn from data."
        query = "What is the relationship between AI and ML?"
        
        app_logger.info(f"\n📝 Testing with context...")
        app_logger.info(f"   Context: {context}")
        app_logger.info(f"   Query: {query}")
        
        response_with_context = llm_service.generate_response(query, context)
        
        app_logger.info(f"\n✅ Context-aware response generated!")
        app_logger.info(f"   Response: {response_with_context}")
        
        # Test streaming
        app_logger.info(f"\n📝 Testing streaming...")
        app_logger.info("   Stream: ", end="")
        
        for chunk in llm_service.generate_response_stream("Tell me a short fact about Python programming."):
            app_logger.info(chunk, end="")
        
        app_logger.info("\n✅ Streaming test complete!")
        
        return True
        
    except Exception as e:
        app_logger.error(f"❌ Chat test failed: {str(e)}")
        return False


def test_gemini_features():
    """Test additional Gemini features"""
    app_logger.info("\n" + "=" * 60)
    app_logger.info("TESTING ADDITIONAL FEATURES")
    app_logger.info("=" * 60)
    
    try:
        # Test summary
        long_text = """
        Artificial Intelligence (AI) is transforming the world in unprecedented ways. 
        Machine learning algorithms are now capable of recognizing patterns in vast amounts of data, 
        enabling applications from medical diagnosis to autonomous vehicles. 
        Deep learning, a subset of machine learning, uses neural networks with multiple layers 
        to process information in ways that mimic the human brain. 
        Natural language processing allows computers to understand and generate human language, 
        powering chatbots, translation services, and content creation tools.
        """
        
        app_logger.info("\n📝 Testing summary generation...")
        summary = llm_service.generate_summary(long_text, max_length=50)
        
        app_logger.info(f"✅ Summary generated!")
        app_logger.info(f"   Summary: {summary}")
        
        # Test keyword extraction
        app_logger.info("\n📝 Testing keyword extraction...")
        keywords = llm_service.extract_keywords(long_text, max_keywords=5)
        
        app_logger.info(f"✅ Keywords extracted!")
        app_logger.info(f"   Keywords: {', '.join(keywords)}")
        
        return True
        
    except Exception as e:
        app_logger.error(f"❌ Features test failed: {str(e)}")
        return False


def main():
    """Run all Gemini tests"""
    app_logger.info("\n🚀 STARTING GEMINI API TESTS")
    app_logger.info("=" * 60)
    
    results = {
        "embeddings": False,
        "chat": False,
        "features": False
    }
    
    # Run tests
    results["embeddings"] = test_gemini_embeddings()
    results["chat"] = test_gemini_chat()
    results["features"] = test_gemini_features()
    
    # Summary
    app_logger.info("\n" + "=" * 60)
    app_logger.info("TEST SUMMARY")
    app_logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        app_logger.info(f"{test_name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        app_logger.info("\n🎉 ALL TESTS PASSED! Gemini API is working correctly.")
        return 0
    else:
        app_logger.info("\n⚠️ SOME TESTS FAILED. Check the errors above.")
        app_logger.info("\nTroubleshooting:")
        app_logger.info("1. Ensure GEMINI_API_KEY is set in .env")
        app_logger.info("2. Check your API key at https://makersuite.google.com/app/apikey")
        app_logger.info("3. Verify you have internet connection")
        app_logger.info("4. Check rate limits (60 RPM for free tier)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
