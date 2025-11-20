# ⚡ QUICK START GUIDE - DAY 2 FEATURES

## 🚀 Run the Backend

```bash
cd C:\Users\hp\Regnova\backend
venv\Scripts\activate
python -m app.main
```

**Server**: http://localhost:8000
**Docs**: http://localhost:8000/api/docs

---

## 🔑 Get Started in 3 Steps

### Step 1: Get Gemini API Key (FREE!)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key
4. Add to `.env`: `GEMINI_API_KEY=your-key-here`

### Step 2: Test Gemini
```bash
python scripts\test_gemini.py
```

### Step 3: Try Enhanced Chat
```bash
# Login first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Copy the access_token, then:
curl -X POST http://localhost:8000/api/chat/v2/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"test",
    "message":"What can you help me with?",
    "mode":"fast"
  }'
```

---

## 🎯 Key Features

### 1. **Dual RAG Modes**
- **Fast Mode**: Quick responses (top 5 results)
- **Accurate Mode**: Deep search (top 10 + reranking)

```python
# In request
"mode": "fast"  # or "accurate"
```

### 2. **SSE Streaming**
Real-time token-by-token responses:

```bash
curl -N http://localhost:8000/api/chat/v2/stream?message=Hello&session_id=test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. **Safety Guards**
- Prompt injection detection
- Hallucination checking
- Automatic source verification

### 4. **Automations**

**Send Email:**
```bash
curl -X POST http://localhost:8000/api/automations/email/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email":"user@example.com",
    "subject":"Test",
    "body":"Hello!"
  }'
```

**Send WhatsApp:**
```bash
curl -X POST http://localhost:8000/api/automations/whatsapp/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number":"+1234567890",
    "message":"Hello from Regnova!"
  }'
```

---

## 📊 All Available Endpoints

### Chat V2 (Enhanced)
- `POST /api/chat/v2/message` - Chat with RAG modes
- `POST /api/chat/v2/stream` - SSE streaming
- `GET /api/chat/v2/modes` - Available modes

### Automations
- `POST /api/automations/email/send` - Send email
- `POST /api/automations/email/rag` - RAG-powered email
- `POST /api/automations/whatsapp/send` - Send WhatsApp
- `POST /api/automations/push/send` - Push notification

### Original Features (Still Available)
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login
- `POST /api/upload/pdf` - Upload PDF
- `POST /api/scrape/url` - Scrape URL
- `POST /api/chat/message` - Basic chat

---

## ⚙️ Configuration

**Minimum Required:**
```env
GEMINI_API_KEY=your-key
SECRET_KEY=your-secret
```

**Full Features:**
```env
# Gemini
GEMINI_API_KEY=your-gemini-key
LLM_MODEL=gemini-1.5-pro

# Gmail
GMAIL_EMAIL=your@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# ***REMOVED***
***REMOVED***_ACCOUNT_SID=your-sid
***REMOVED***_***REMOVED***=your-token
***REMOVED***_WHATSAPP_FROM=whatsapp:+14155238886

# RAG
RAG_MODE=accurate
RAG_RERANK=true
```

---

## 🧪 Test Everything

```bash
# 1. Test Gemini
python scripts\test_gemini.py

# 2. Test embeddings
python scripts\test_embeddings.py

# 3. Test PDF processing
python scripts\test_pdf.py sample.pdf

# 4. Test web scraping
python scripts\test_web_scraping.py https://example.com

# 5. Verify setup
python scripts\verify_setup.py
```

---

## 🎯 What's Working

✅ **DAY 1 Features**
- JWT Authentication
- PDF Upload & OCR
- Web Scraping
- Vector Store (FAISS)
- Basic RAG Chat

✅ **DAY 2 Features**
- Enhanced Chat with SSE
- Gemini API Integration
- Dual RAG Modes
- Reranking Engine
- Prompt Injection Guard
- Hallucination Detection
- Gmail Automation
- WhatsApp Automation
- Push Notifications

---

## 🚨 Troubleshooting

### "Gemini API key not configured"
Add to `.env`: `GEMINI_API_KEY=your-key`

### "Module not found"
```bash
pip install -r requirements.txt --force-reinstall
```

### "Port already in use"
Change port in `.env`: `PORT=8001`

### Rate limiting errors
Increase in `.env`: `RATE_LIMIT_PER_MINUTE=50`

---

## 📖 Documentation

- **API Docs**: http://localhost:8000/api/docs
- **Full Setup**: `SETUP.md`
- **DAY 2 Guide**: `DAY2_SETUP.md`
- **Verification**: `DAY2_FINAL_VERIFICATION.md`

---

## 🎊 Ready for Frontend!

Backend is complete. Type **"start frontend"** to build the UI!

---

**Quick Help**: http://localhost:8000/api/docs
