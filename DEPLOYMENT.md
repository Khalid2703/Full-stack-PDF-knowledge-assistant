# 🚀 Deployment Guide for Render

This guide walks you through deploying Regnova on Render as separate backend and frontend services.

## 📋 Prerequisites

1. GitHub account
2. Render account (sign up at [render.com](https://render.com))
3. Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🔧 Step 1: Prepare Your Repository

### 1.1 Initialize Git Repository

```bash
# Navigate to project root
cd /path/to/Regnova

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Regnova Knowledge Assistant"

# Rename branch to main
git branch -M main

# Add remote (replace with your repo URL)
git remote add origin https://github.com/Khalid2703/Full-stack-PDF-knowledge-assistant.git

# Push to GitHub
git push -u origin main
```

### 1.2 Create Required Files

Ensure you have:
- ✅ `README.md` (root)
- ✅ `.gitignore` (root)
- ✅ `backend/Dockerfile`
- ✅ `frontend/Dockerfile`
- ✅ `backend/requirements.txt`
- ✅ `frontend/package.json`

## 🎯 Step 2: Deploy Backend Service

### 2.1 Create Web Service for Backend

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository: `Full-stack-PDF-knowledge-assistant`

### 2.2 Configure Backend Service

**Basic Settings:**
- **Name:** `regnova-backend`
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Docker`
- **Dockerfile Path:** `backend/Dockerfile` (or just `Dockerfile` since root is backend)
- **Docker Context:** `backend`
- **Command:** Leave empty (handled by Dockerfile)

**Environment Variables:**
Add these in the Environment tab:

```bash
# Database (SQLite for now, or use Render PostgreSQL)
DATABASE_URL=sqlite:///./regnova.db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# Application Settings
DEBUG=False
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Embedding Model
EMBEDDING_MODEL=models/embedding-001
EMBEDDING_DIMENSION=768

# LLM Model
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# RAG Configuration
RAG_TOP_K=5
RAG_RERANK=True
RAG_MODE=accurate

# File Storage
UPLOAD_DIR=./storage/uploads
VECTOR_STORE_PATH=./storage/vector_store
MAX_FILE_SIZE=50000000
```

**Persistent Disk (Important!):**
1. Go to **"Disks"** tab
2. Click **"Mount Disk"**
3. **Name:** `regnova-storage`
4. **Mount Path:** `/app/storage`
5. **Size:** 1GB (or more if needed)

This ensures uploaded files and vector store persist across deployments.

### 2.3 Deploy Backend

1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes)
3. Note the service URL (e.g., `https://regnova-backend.onrender.com`)

## 🎨 Step 3: Deploy Frontend Service

### 3.1 Create Web Service for Frontend

1. Click **"New +"** → **"Web Service"**
2. Connect same repository: `Full-stack-PDF-knowledge-assistant`

### 3.2 Configure Frontend Service

**Basic Settings:**
- **Name:** `regnova-frontend`
- **Region:** Same as backend
- **Branch:** `main`
- **Root Directory:** `frontend`
- **Runtime:** `Docker`
- **Dockerfile Path:** `frontend/Dockerfile`
- **Docker Context:** `frontend`
- **Command:** Leave empty

**Environment Variables:**
```bash
# Production
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# API URL (CRITICAL - use your backend service URL)
NEXT_PUBLIC_API_URL=https://regnova-backend.onrender.com
```

**Build Command:**
```bash
npm run build
```

**Start Command:**
```bash
node server.js
```

### 3.3 Update Frontend Dockerfile (if needed)

Ensure your `frontend/Dockerfile` supports standalone output. Check if `next.config.js` has:

```javascript
output: 'standalone'
```

### 3.4 Deploy Frontend

1. Click **"Create Web Service"**
2. Wait for build
3. Note the frontend URL (e.g., `https://regnova-frontend.onrender.com`)

## 🔗 Step 4: Update CORS Settings (Backend)

After both services are deployed:

1. Go to backend service → **Environment**
2. Add CORS origin:
```bash
CORS_ORIGINS=https://regnova-frontend.onrender.com
```

Or update `backend/app/main.py` to allow your frontend domain.

## ✅ Step 5: Verify Deployment

1. Visit your frontend URL
2. Test registration/login
3. Upload a test PDF
4. Try asking a question

## 🔧 Step 6: Production Optimizations

### 6.1 Use PostgreSQL (Recommended)

Instead of SQLite:

1. Create **PostgreSQL** database on Render
2. Get connection string
3. Update backend `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://user:pass@host/dbname
```

### 6.2 Update Backend for PostgreSQL

Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

### 6.3 Health Check Endpoint

Ensure backend has `/health` endpoint (already in Dockerfile healthcheck).

## 📊 Monitoring & Logs

- **Logs:** Available in Render dashboard for each service
- **Metrics:** CPU, Memory, Request rate in dashboard
- **Alerts:** Set up email alerts for service failures

## 🔄 Updating Deployment

To deploy updates:

1. Push changes to GitHub:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

2. Render auto-deploys on push (or manually trigger in dashboard)

## 🐛 Troubleshooting

### Backend Issues

**Build Fails:**
- Check Dockerfile syntax
- Verify requirements.txt
- Check logs in Render dashboard

**Service Crashes:**
- Check environment variables
- Verify database connection
- Check disk space

### Frontend Issues

**Build Fails:**
- Check package.json
- Verify Node version (18+)
- Check Next.js config

**API Connection Errors:**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Ensure backend service is running

### Common Issues

**"Module not found":**
- Rebuild service (Settings → Clear build cache)

**"Disk full":**
- Increase disk size or clean old files

**"Timeout":**
- Render free tier has cold starts (spins down after 15min inactivity)
- Upgrade to paid tier for always-on

## 💰 Cost Estimation

**Free Tier:**
- ✅ 750 hours/month
- ⚠️ Spins down after 15min inactivity
- ⚠️ 512MB RAM limit

**Paid Tier:**
- $7-25/month per service
- Always on
- More RAM & resources

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` to random string
- [ ] Use strong `JWT_SECRET_KEY`
- [ ] Never commit `.env` files
- [ ] Use HTTPS (automatic on Render)
- [ ] Enable rate limiting
- [ ] Regularly update dependencies

## 📞 Support

- [Render Docs](https://render.com/docs)
- [Render Status](https://status.render.com)
- Check application logs in Render dashboard

---

**Ready to deploy?** Follow steps 1-6 above, and you'll have Regnova running in production! 🚀

