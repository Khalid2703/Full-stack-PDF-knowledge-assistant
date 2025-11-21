# 🔐 Environment Variables for Render Deployment

## 📋 Essential Variables (Must Add)

These are **REQUIRED** for the app to work. Add these first:

### Backend Service - Essential Variables

```bash
# ============================================
# REQUIRED - Core Application
# ============================================
ENVIRONMENT=production
DEBUG=False
PORT=8000

# ============================================
# REQUIRED - Security (Generate Strong Secrets!)
# ============================================
# Generate secrets using: openssl rand -hex 32
SECRET_KEY=<generate-random-32-char-string>
JWT_SECRET_KEY=<generate-random-32-char-string>

# ============================================
# REQUIRED - Database
# ============================================
# For SQLite (simple, but not ideal for production):
DATABASE_URL=sqlite:///./regnova.db

# OR for PostgreSQL (recommended - create DB on Render first):
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# ============================================
# REQUIRED - Gemini API
# ============================================
GEMINI_API_KEY=your-actual-gemini-api-key-here

# ============================================
# REQUIRED - CORS (Update after frontend is deployed)
# ============================================
# Set this AFTER you deploy frontend, using your frontend URL:
CORS_ORIGINS=https://your-frontend-service.onrender.com
```

---

## 🎯 Recommended Variables (Add for Better Performance)

These improve functionality but have defaults:

```bash
# ============================================
# RECOMMENDED - Application Config
# ============================================
APP_NAME=Regnova Knowledge Assistant
APP_VERSION=1.0.0
HOST=0.0.0.0

# ============================================
# RECOMMENDED - RAG Settings
# ============================================
RAG_MODE=accurate          # Options: fast, accurate
RAG_TOP_K=5                # Number of chunks to retrieve
RAG_RERANK=True            # Enable reranking for better results

# ============================================
# RECOMMENDED - LLM Settings
# ============================================
LLM_MODEL=gemini-1.5-pro   # Or gemini-pro
LLM_TEMPERATURE=0.7        # 0.0-1.0 (lower = more focused)
LLM_MAX_TOKENS=2048        # Max response length

# ============================================
# RECOMMENDED - Embedding Model
# ============================================
EMBEDDING_MODEL=models/embedding-001
EMBEDDING_DIMENSION=768

# ============================================
# RECOMMENDED - File Storage
# ============================================
MAX_FILE_SIZE=50000000     # 50MB in bytes
ALLOWED_EXTENSIONS=pdf,txt,doc,docx
```

---

## ⚙️ Optional Variables (Only if Needed)

Only add these if you're using those features:

### Safety Features (Already enabled by default)
```bash
ENABLE_PROMPT_INJECTION_GUARD=True
ENABLE_HALLUCINATION_GUARD=True
```

### Rate Limiting
```bash
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=10
```

### Automation Features (Only if using)
```bash
# Gmail
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# ***REMOVED*** WhatsApp
***REMOVED***_ACCOUNT_SID=your-sid
***REMOVED***_***REMOVED***=your-token
***REMOVED***_WHATSAPP_FROM=whatsapp:+1234567890

# OneSignal
ONESIGNAL_APP_ID=your-app-id
ONESIGNAL_REST_API_KEY=your-api-key
```

---

## 📝 Frontend Service - Essential Variables

```bash
# ============================================
# REQUIRED
# ============================================
NODE_ENV=production

# ============================================
# REQUIRED - API URL (Use your backend service URL)
# ============================================
NEXT_PUBLIC_API_URL=https://your-backend-service.onrender.com

# ============================================
# OPTIONAL
# ============================================
NEXT_TELEMETRY_DISABLED=1
```

---

## 🚀 Quick Setup Guide for Render

### Step 1: Backend Environment Variables

In Render dashboard → Your Backend Service → Environment tab:

**Minimum Required (7 variables):**
```
ENVIRONMENT=production
DEBUG=False
PORT=8000
SECRET_KEY=<generate-random-secret>
JWT_SECRET_KEY=<generate-random-secret>
GEMINI_API_KEY=<your-gemini-key>
DATABASE_URL=sqlite:///./regnova.db
```

**After frontend deploys, add:**
```
CORS_ORIGINS=https://your-frontend.onrender.com
```

### Step 2: Frontend Environment Variables

In Render dashboard → Your Frontend Service → Environment tab:

**Required (2 variables):**
```
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 🔑 How to Generate Secure Secrets

### Option 1: Using OpenSSL (if installed)
```bash
openssl rand -hex 32
```

### Option 2: Using Python
```python
import secrets
print(secrets.token_hex(32))
```

### Option 3: Using Node.js
```javascript
require('crypto').randomBytes(32).toString('hex')
```

### Option 4: Online Generator
Visit: https://generate-secret.vercel.app/32

---

## ✅ Deployment Checklist

- [ ] `ENVIRONMENT=production` set
- [ ] `GEMINI_API_KEY` added (valid key)
- [ ] `SECRET_KEY` generated (random 32+ chars)
- [ ] `JWT_SECRET_KEY` generated (random 32+ chars)
- [ ] `DATABASE_URL` configured (SQLite or PostgreSQL)
- [ ] `CORS_ORIGINS` set to frontend URL (after frontend deploys)
- [ ] Frontend `NEXT_PUBLIC_API_URL` set to backend URL
- [ ] Persistent disk mounted at `/app/storage` (for backend)

---

## 🐛 Common Issues

**"Invalid API key"**
- ✅ Check `GEMINI_API_KEY` is correct
- ✅ No extra spaces or quotes
- ✅ Key is active in Google AI Studio

**"CORS error"**
- ✅ `CORS_ORIGINS` includes your frontend URL exactly
- ✅ No trailing slashes
- ✅ Frontend URL matches what's in browser

**"Database error"**
- ✅ `DATABASE_URL` format is correct
- ✅ For PostgreSQL: connection string is valid
- ✅ Disk is mounted for SQLite persistence

**"Service won't start"**
- ✅ `PORT=8000` is set (Render requirement)
- ✅ `HOST=0.0.0.0` is set (Render requirement)
- ✅ All required variables are present

---

## 📊 Variable Priority

1. **🔴 CRITICAL** - App won't work without these
   - GEMINI_API_KEY
   - SECRET_KEY
   - JWT_SECRET_KEY
   - DATABASE_URL
   - ENVIRONMENT

2. **🟡 IMPORTANT** - App works but not optimally
   - CORS_ORIGINS
   - NEXT_PUBLIC_API_URL (frontend)

3. **🟢 OPTIONAL** - Nice to have
   - Automation variables
   - Custom LLM settings
   - Rate limiting config

---

## 💡 Pro Tips

1. **Never commit secrets** - Use Render environment variables only
2. **Update CORS after both services deploy** - Frontend URL may change
3. **Use PostgreSQL for production** - SQLite can have concurrency issues
4. **Test environment variables** - Use `/health` endpoint to verify
5. **Rotate secrets regularly** - Change SECRET_KEY periodically

---

**Ready to deploy?** Copy the essential variables above into Render! 🚀

