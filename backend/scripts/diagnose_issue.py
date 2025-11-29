
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.utils.logger import app_logger


def check_environment():
    """Check environment variables"""
    print("\n" + "="*60)
    print("🔍 ENVIRONMENT VARIABLES CHECK")
    print("="*60)
    
    checks = {
        "GEMINI_API_KEY": settings.GEMINI_API_KEY,
        "OPENAI_API_KEY": settings.OPENAI_API_KEY,
        "LLM_MODEL": settings.LLM_MODEL,
        "VECTOR_STORE_PATH": settings.VECTOR_STORE_PATH,
        "DATABASE_URL": settings.DATABASE_URL,
    }
    
    for key, value in checks.items():
        if value:
            if "KEY" in key:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {key}: {masked}")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: NOT SET")
    
    return all([checks["GEMINI_API_KEY"], checks["LLM_MODEL"]])


def check_openai():
    """Test OpenAI API connection"""
    print("\n" + "="*60)
    print("🤖 OPENAI API CHECK")
    print("="*60)
    
    try:
        from openai import OpenAI
        print(f"✅ openai package: INSTALLED")
        
        # Check version
        import pkg_resources
        version = pkg_resources.get_distribution("openai").version
        print(f"📦 Version: {version}")
        
        if not settings.OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY not set (will use Gemini fallback)")
            return False
        
        # Test connection
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print(f"✅ API key configured")
        
        # Test models list
        models = client.models.list()
        print(f"✅ Connection successful")
        
        # Test generation
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=50
        )
        print(f"✅ Test generation successful")
        print(f"📝 Response: {response.choices[0].message.content[:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ openai package not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False


def check_gemini():
    """Test Gemini API connection"""
    print("\n" + "="*60)
    print("🤖 GEMINI API CHECK (Fallback)")
    print("="*60)
    
    try:
        import google.generativeai as genai
        print(f"✅ google-generativeai package: INSTALLED")
        
        # Check version
        import pkg_resources
        version = pkg_resources.get_distribution("google-generativeai").version
        print(f"📦 Version: {version}")
        
        if not settings.GEMINI_API_KEY:
            print("⚠️  GEMINI_API_KEY not set (OpenAI will be primary if available)")
            return False
        
        # Configure
        genai.configure(api_key=settings.GEMINI_API_KEY)
        print(f"✅ API key configured")
        
        # Test model
        model = genai.GenerativeModel(settings.LLM_MODEL)
        print(f"✅ Model initialized: {settings.LLM_MODEL}")
        
        # Test generation
        response = model.generate_content("Say hello")
        print(f"✅ Test generation successful")
        print(f"📝 Response: {response.text[:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ google-generativeai not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False


def check_faiss():
    """Check FAISS installation and vector store"""
    print("\n" + "="*60)
    print("🗂️  FAISS VECTOR STORE CHECK")
    print("="*60)
    
    try:
        import faiss
        print(f"✅ faiss-cpu package: INSTALLED")
        
        # Check if index exists
        index_path = os.path.join(settings.VECTOR_STORE_PATH, "faiss_index.bin")
        map_path = os.path.join(settings.VECTOR_STORE_PATH, "document_map.pkl")
        
        if os.path.exists(index_path):
            print(f"✅ FAISS index found: {index_path}")
            
            # Try loading
            index = faiss.read_index(index_path)
            print(f"✅ Index loaded: {index.ntotal} vectors")
        else:
            print(f"⚠️  FAISS index not found: {index_path}")
            print(f"   This is normal on first run. Index will be created when you upload documents.")
        
        if os.path.exists(map_path):
            print(f"✅ Document map found: {map_path}")
        else:
            print(f"⚠️  Document map not found (normal on first run)")
        
        return True
        
    except ImportError as e:
        print(f"❌ faiss-cpu not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ FAISS error: {e}")
        return False


def check_answer_generator():
    """Test answer generator initialization"""
    print("\n" + "="*60)
    print("💬 ANSWER GENERATOR CHECK")
    print("="*60)
    
    try:
        from app.chat.answer_generator import answer_generator
        
        if answer_generator.llm_available:
            print(f"✅ Answer generator: INITIALIZED")
            from app.services.llm_service import llm_service
            if llm_service.use_openai:
                print(f"✅ Using: OpenAI GPT-4o-mini (PRIMARY)")
            else:
                print(f"✅ Using: Gemini {settings.LLM_MODEL} (FALLBACK)")
            
            # Test generation with mock data
            test_query = "What is machine learning?"
            test_context = "Machine learning is a subset of artificial intelligence."
            test_chunks = [{
                'file_id': 1,
                'filename': 'test.pdf',
                'chunk_index': 0,
                'content': test_context,
                'page_number': 1,
                'relevance_score': 0.9
            }]
            
            print(f"🧪 Testing answer generation...")
            answer, metadata = answer_generator.generate_answer(
                query=test_query,
                context=test_context,
                chunks=test_chunks,
                use_citations=True
            )
            
            print(f"✅ Answer generated successfully")
            print(f"📝 Answer preview: {answer[:100]}...")
            print(f"📊 Metadata: {metadata}")
            
            return True
        else:
            print(f"❌ Answer generator not available")
            print(f"   Reason: No LLM service available (need OpenAI or Gemini)")
            return False
        
    except Exception as e:
        print(f"❌ Answer generator error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_database():
    """Check database connection"""
    print("\n" + "="*60)
    print("🗄️  DATABASE CHECK")
    print("="*60)
    
    try:
        from app.database import engine, SessionLocal
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Database connection: SUCCESS")
        
        # Test session
        db = SessionLocal()
        db.close()
        print(f"✅ Session creation: SUCCESS")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✅ Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def main():
    """Run all diagnostic checks"""
    print("\n" + "="*60)
    print("🔧 REGNOVA DIAGNOSTIC TOOL")
    print("="*60)
    print(f"Running diagnostics for: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    
    results = {
        "Environment": check_environment(),
        "OpenAI API": check_openai(),
        "Gemini API": check_gemini(),
        "FAISS": check_faiss(),
        "Answer Generator": check_answer_generator(),
        "Database": check_database(),
    }
    
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("Your system should be working correctly.")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("Please review the errors above and:")
        print("1. Set missing environment variables")
        print("2. Install missing packages: pip install -r requirements.txt")
        print("3. Verify API keys are valid")
        print("4. Check network connectivity")
    print("="*60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
