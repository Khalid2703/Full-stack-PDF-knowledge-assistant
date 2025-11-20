# Complete Setup Guide

## Prerequisites

- Python 3.9+
- pip
- Tesseract OCR (for scanned PDFs)
- Git

## Step-by-Step Setup

### 1. Install Tesseract OCR

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH
# Default location: C:\Program Files\Tesseract-OCR\tesseract.exe
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 2. Clone and Setup Project

```bash
cd C:\Users\hp\Regnova\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

**Required Settings:**
```env
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=sqlite:///./regnova.db
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

### 5. Test Services (Optional)

```bash
# Test embeddings
python scripts/test_embeddings.py

# Test PDF extraction (provide a PDF file path)
python scripts/test_pdf.py path/to/test.pdf

# Test web scraping
python scripts/test_web_scraping.py https://example.com
```

### 6. Run the Server

```bash
python -m app.main
```

Or with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verify Installation

Open browser and visit:
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

### 8. Create First User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Admin User\", \"email\": \"admin@regnova.com\", \"password\": \"admin123\", \"organization\": \"Regnova\"}"
```

## Troubleshooting

### Issue: Tesseract not found
**Solution:** 
```env
# Add to .env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Issue: Port already in use
**Solution:**
```bash
# Change port in .env
PORT=8001
```

### Issue: Database locked
**Solution:**
```bash
# Delete database and reinitialize
del regnova.db
python scripts/init_db.py
```

### Issue: Import errors
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Module not found error
**Solution:**
```bash
# Make sure you're in the virtual environment
venv\Scripts\activate

# Install missing packages
pip install <package-name>
```

### Issue: Embedding model download fails
**Solution:**
```bash
# The model will download automatically on first run
# Ensure you have internet connection
# Model will be cached in: C:\Users\hp\.cache\torch\sentence_transformers\
```

## Production Deployment

### 1. Use PostgreSQL

```env
DATABASE_URL=postgresql://user:password@localhost:5432/regnova_db
```

Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

### 2. Set Environment to Production

```env
ENVIRONMENT=production
DEBUG=False
```

### 3. Generate Strong Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. Use Gunicorn

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. Setup Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/upload/pdf {
        client_max_body_size 50M;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## Docker Setup (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t regnova-backend .
docker run -p 8000:8000 regnova-backend
```

## Next Steps

1. ✅ Backend is ready
2. ⏭️ Proceed to frontend development (DAY 2)
3. ⏭️ Set up authentication flow
4. ⏭️ Build UI components
5. ⏭️ Integrate with backend APIs

## Support

For issues or questions:
- Check logs in: `logs/app.log`
- Review API docs: http://localhost:8000/api/docs
- Test endpoints with Postman
