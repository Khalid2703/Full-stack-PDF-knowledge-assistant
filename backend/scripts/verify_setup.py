"""
Quick verification script to check if all files exist
Run this to verify backend setup is complete
"""

import os
import sys

def check_file_exists(filepath):
    """Check if a file exists and print status"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def main():
    """Verify all backend files exist"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.dirname(base_path)
    
    print("=" * 60)
    print("REGNOVA BACKEND VERIFICATION")
    print("=" * 60)
    print(f"\nBackend Path: {backend_path}\n")
    
    files_to_check = [
        # Root files
        ".env.example",
        "README.md",
        "SETUP.md",
        "COMPLETION_CHECKLIST.md",
        "requirements.txt",
        
        # App core
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/database.py",
        
        # Models
        "app/models/__init__.py",
        "app/models/user.py",
        "app/models/file.py",
        "app/models/chunk.py",
        "app/models/chat.py",
        
        # Schemas
        "app/schemas/__init__.py",
        "app/schemas/user.py",
        "app/schemas/file.py",
        "app/schemas/chat.py",
        
        # Routes
        "app/routes/__init__.py",
        "app/routes/auth.py",
        "app/routes/upload.py",
        "app/routes/scrape.py",
        "app/routes/chat.py",
        
        # Services
        "app/services/__init__.py",
        "app/services/auth_service.py",
        "app/services/pdf_service.py",
        "app/services/web_service.py",
        "app/services/embedding_service.py",
        "app/services/rag_service.py",
        "app/services/metadata_service.py",
        
        # Utils
        "app/utils/__init__.py",
        "app/utils/security.py",
        "app/utils/logger.py",
        "app/utils/helpers.py",
        
        # Scripts
        "scripts/init_db.py",
        "scripts/test_embeddings.py",
        "scripts/test_pdf.py",
        "scripts/test_web_scraping.py",
    ]
    
    folders_to_check = [
        "storage/uploads",
        "storage/vector_store",
        "logs",
    ]
    
    print("Checking Files:")
    print("-" * 60)
    
    all_files_exist = True
    for file in files_to_check:
        full_path = os.path.join(backend_path, file)
        exists = check_file_exists(file)
        if not exists:
            all_files_exist = False
    
    print("\nChecking Folders:")
    print("-" * 60)
    
    all_folders_exist = True
    for folder in folders_to_check:
        full_path = os.path.join(backend_path, folder)
        exists = os.path.isdir(full_path)
        status = "✅" if exists else "❌"
        print(f"{status} {folder}/")
        if not exists:
            all_folders_exist = False
    
    print("\n" + "=" * 60)
    if all_files_exist and all_folders_exist:
        print("✅ ALL FILES AND FOLDERS VERIFIED SUCCESSFULLY!")
        print("=" * 60)
        print("\n🚀 Backend is ready to run!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure .env file: copy .env.example .env")
        print("3. Initialize database: python scripts/init_db.py")
        print("4. Run server: python -m app.main")
        print("\n📚 Documentation:")
        print("- README.md - Full documentation")
        print("- SETUP.md - Setup instructions")
        print("- API Docs: http://localhost:8000/api/docs")
        return 0
    else:
        print("❌ SOME FILES OR FOLDERS ARE MISSING!")
        print("=" * 60)
        print("\nPlease check the missing items above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
