# Regnova Knowledge Assistant - Backend

Production-grade FastAPI backend for Universal PDF + Web Knowledge Assistant with RAG capabilities.

## Features

✅ JWT Authentication (Register/Login)  
✅ PDF Upload & Processing (Text + OCR)  
✅ URL Scraping & Content Extraction  
✅ Vector Store (FAISS) with Semantic Search  
✅ RAG Pipeline with Source Grounding  
✅ Smart Metadata Extraction (TOC, Entities)  
✅ Chat Interface with Conversation History  
✅ File Management & Deletion  
✅ Comprehensive Error Handling & Logging  

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env with your configuration
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Run the Server

```bash
python -m app.main
```

Or with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### File Upload
- `POST /api/upload/pdf` - Upload PDF file
- `GET /api/upload/files` - List all user files
- `GET /api/upload/files/{file_id}/metadata` - Get file metadata
- `DELETE /api/upload/files/{file_id}` - Delete file

### Web Scraping
- `POST /api/scrape/url` - Scrape URL content

### Chat
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history/{session_id}` - Get chat history
- `GET /api/chat/sessions` - List all sessions
- `DELETE /api/chat/sessions/{session_id}` - Delete session

### Health
- `GET /health` - Health check

## Testing with cURL

### 1. Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "organization": "Acme Corp"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

Save the `access_token` from the response.

### 3. Upload PDF

```bash
curl -X POST "http://localhost:8000/api/upload/pdf" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/document.pdf"
```

### 4. Scrape URL

```bash
curl -X POST "http://localhost:8000/api/scrape/url" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "extract_metadata": true
  }'
```

### 5. Chat with RAG

```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "message": "What are the key points in the uploaded documents?",
    "use_rag": true
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── file.py
│   │   ├── chunk.py
│   │   └── chat.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── file.py
│   │   └── chat.py
│   ├── routes/                 # API routes
│   │   ├── auth.py
│   │   ├── upload.py
│   │   ├── scrape.py
│   │   └── chat.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── pdf_service.py
│   │   ├── web_service.py
│   │   ├── embedding_service.py
│   │   ├── rag_service.py
│   │   └── metadata_service.py
│   └── utils/                  # Utilities
│       ├── security.py
│       ├── logger.py
│       └── helpers.py
├── storage/                    # File storage
│   ├── uploads/
│   └── vector_store/
├── logs/                       # Application logs
├── scripts/                    # Utility scripts
├── requirements.txt
├── .env.example
└── README.md
```

## Database Schema

### Users
- id, name, email, organization, hashed_password
- is_active, is_verified, created_at, updated_at

### Files
- id, user_id, filename, original_filename, file_type
- file_path, url, file_size, page_count
- title, author, is_processed, uploaded_at

### Chunks
- id, file_id, chunk_index, content
- page_number, section_title
- embedding_vector, vector_id

### Chats
- id, user_id, session_id, role, content
- sources, relevance_scores, created_at

## Environment Variables

```env
# Application
APP_NAME=Regnova Knowledge Assistant
DEBUG=True

# Database
DATABASE_URL=sqlite:///./regnova.db

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (optional)
***REMOVED***_API_KEY=***REMOVED***your-key

# Storage
UPLOAD_DIR=./storage/uploads
VECTOR_STORE_PATH=./storage/vector_store
MAX_FILE_SIZE=50000000

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Development Notes

- SQLite is used by default for development
- For production, use PostgreSQL
- Vector embeddings are stored in FAISS index
- OCR requires Tesseract installation
- All passwords are hashed with bcrypt
- JWT tokens expire after 30 minutes (configurable)

## Next Steps

1. Integrate OpenAI API for better chat responses
2. Add Redis for caching
3. Implement rate limiting
4. Add comprehensive tests
5. Set up CI/CD pipeline
6. Deploy to Render

## License

MIT License
