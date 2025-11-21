# 📋 FINAL DEPLOYMENT CHECKLIST - 4 HOURS

## ⏰ TIMELINE

- **Hour 1:** Environment variables + Backend deploy (30 min)
- **Hour 2:** Frontend deploy (15 min)
- **Hour 3:** Testing + Documentation (45 min)
- **Hour 4:** Final submission (30 min)

---

## ✅ HOUR 1: DEPLOY BACKEND (30 MINUTES)

### Step 1: Create Render Account (2 min)

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize access

### Step 2: Create PostgreSQL Database (3 min)

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `regnova-db`
3. Region: **Oregon (US West)**
4. Plan: **Free**
5. Click **"Create Database"**
6. **Copy "Internal Database URL"** - you'll need it!

### Step 3: Create Web Service (5 min)

1. Click **"New +"** → **"Web Service"**
2. Connect GitHub repo
3. Configure:
   - **Name:** `regnova-backend`
   - **Region:** Oregon (US West)
   - **Branch:** main
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

### Step 4: Add Environment Variables (10 min)

Click **"Environment"** tab and add these **EXACT** variables:

```env
# === REQUIRED (Must have) ===
SECRET_KEY=generate-new-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=[Paste Internal Database URL from Step 2]
ENVIRONMENT=production
DEBUG=False

# === SETTINGS ===
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7
RAG_TOP_K=10
RAG_RERANK=true
ENABLE_PROMPT_INJECTION_GUARD=true
ENABLE_HALLUCINATION_GUARD=true
```

**To generate SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Deploy (10 min)

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Check logs for errors
4. Your API will be at: `https://regnova-backend.onrender.com`

### Step 6: Test Backend

```bash
curl https://regnova-backend.onrender.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "app_name": "Regnova Knowledge Assistant",
  "version": "1.0.0"
}
```

---

## ✅ HOUR 2: DEPLOY FRONTEND (15 MINUTES)

### Step 1: Update Frontend Config (2 min)

Create `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://regnova-backend.onrender.com
```

### Step 2: Vercel Deployment (5 min)

**Option A: Vercel CLI**

```bash
npm i -g vercel
cd frontend
vercel --prod
```

**Option B: Vercel Dashboard** (Recommended)

1. Go to https://vercel.com
2. Click **"Add New..."** → **"Project"**
3. Import from GitHub
4. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
5. Add Environment Variable:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://regnova-backend.onrender.com`
6. Click **"Deploy"**

### Step 3: Test Frontend (3 min)

1. Visit your Vercel URL
2. Should see landing page
3. Try login/register
4. Test chat interface

### Step 4: Update CORS (5 min)

Update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Push changes:

```bash
git add .
git commit -m "Update CORS for production"
git push
```

Render will auto-redeploy!

---

## ✅ HOUR 3: TESTING & DOCS (45 MINUTES)

### Testing Checklist (20 min)

Test each feature:

- [ ] Landing page loads
- [ ] Register new user
- [ ] Login works
- [ ] Upload PDF (test with your retailing PDF)
- [ ] PDF shows "Ready" status
- [ ] Navigate to chat
- [ ] Ask question, get response with sources
- [ ] Export chat as JSON
- [ ] Export chat as PDF
- [ ] Logout works

### Documentation Updates (25 min)

1. **Update README.md** with live URLs
2. **Test all curl commands** in docs
3. **Screenshot key features**
4. **Verify all deliverables**

---

## ✅ HOUR 4: FINAL SUBMISSION (30 MINUTES)

### Final Checklist

#### Deliverables ✅

- [ ] GitHub repo with clear commits ✅
- [ ] README with instructions ✅
- [ ] Architecture diagram ✅
- [ ] Tech justification ✅
- [ ] Security document ✅
- [ ] Live URL (Vercel frontend)
- [ ] Live API (Render backend)

#### Features ✅

- [ ] Embeddings-based RAG ✅
- [ ] Streamed responses (basic) ✅
- [ ] Fallback model ✅
- [ ] Error handling ✅
- [ ] Prompt injection guard ✅
- [ ] Hallucination guard ✅
- [ ] Reranking ✅
- [ ] JWT Auth ✅
- [ ] Export JSON ✅
- [ ] Export PDF ✅
- [ ] Docker container ✅
- [ ] Deployed ✅

### Submission URLs

Prepare these URLs:

```
Frontend (User Portal): https://your-app.vercel.app
Backend API: https://regnova-backend.onrender.com
GitHub Repo: https://github.com/Khalid2703/Full-stack-PDF-knowledge-assistant
API Docs: https://regnova-backend.onrender.com/api/docs
```

---

## 🚨 CRITICAL: ENVIRONMENT VARIABLES

### Backend (Render) - MINIMUM Required:

```env
SECRET_KEY=<generate-new-one>
GEMINI_API_KEY=<your-api-key>
DATABASE_URL=<render-provides-this>
ENVIRONMENT=production
DEBUG=False
LLM_MODEL=gemini-1.5-pro
```

### Optional (Add only if using):

```env
# Gmail
GMAIL_EMAIL=your@gmail.com
GMAIL_APP_PASSWORD=app-password

# WhatsApp
***REMOVED***_ACCOUNT_SID=AC...
***REMOVED***_***REMOVED***=...
***REMOVED***_WHATSAPP_FROM=whatsapp:+14155238886
```

**DON'T ADD OPTIONAL ONES** unless you set them up!

---

## 🎯 WHAT TO SKIP (Save Time!)

### Skip for now:

- ❌ Gmail automation (optional)
- ❌ WhatsApp automation (optional)
- ❌ Push notifications (optional)
- ❌ SSE streaming (basic version works)
- ❌ Redis caching
- ❌ Advanced analytics

### Focus on:

- ✅ Core chat functionality
- ✅ PDF upload & processing
- ✅ RAG with citations
- ✅ Export features
- ✅ Security guards
- ✅ Deployment working

---

## 🐛 QUICK FIXES

### Backend won't deploy?

- Check logs in Render dashboard
- Verify DATABASE_URL is set
- Check GEMINI_API_KEY is valid

### Frontend won't connect?

- Check NEXT_PUBLIC_API_URL is correct
- Verify CORS settings in backend
- Check browser console for errors

### Chat not working?

- Make sure PDFs uploaded and processed
- Check backend logs
- Verify Gemini API key is valid

---

## 📞 FINAL CHECKLIST

Before submission:

1. [ ] Both deployments are live
2. [ ] Can register and login
3. [ ] Can upload PDF
4. [ ] Chat returns answers with sources
5. [ ] Export buttons work
6. [ ] All docs pushed to GitHub
7. [ ] URLs ready to submit

---

## 🎉 YOU'RE READY!

**Timeline:**

- ⏱️ Hour 1: Backend deployed ✅
- ⏱️ Hour 2: Frontend deployed ✅
- ⏱️ Hour 3: Everything tested ✅
- ⏱️ Hour 4: Docs complete, submitted ✅

**Your submission:**

```
Project: Regnova Knowledge Assistant
Frontend: https://regnova.vercel.app
Backend: https://regnova-backend.onrender.com
GitHub: https://github.com/Khalid2703/Full-stack-PDF-knowledge-assistant

All deliverables complete ✅
```

**GO DEPLOY! YOU'VE GOT THIS! 🚀**
