# 🚀 RENDER DEPLOYMENT GUIDE - COMPLETE

## ⚡ QUICK DEPLOY (15 Minutes)

### Prerequisites
- ✅ GitHub repo pushed
- ✅ Render account created
- ✅ Gemini API key ready

---

## 📋 RENDER ENVIRONMENT VARIABLES

### ESSENTIAL (Required)
Copy these to Render environment variables:

```env
# === CORE SETTINGS ===
SECRET_KEY=generate-a-new-secret-key-here
ENVIRONMENT=production
DEBUG=False

# === GEMINI API ===
GEMINI_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0.7

# === DATABASE ===
DATABASE_URL=postgresql://user:password@host/db
# Render will provide this automatically

# === RAG CONFIGURATION ===
RAG_TOP_K=10
RAG_RERANK=true
ENABLE_PROMPT_INJECTION_GUARD=true
ENABLE_HALLUCINATION_GUARD=true

# === STORAGE ===
UPLOAD_DIR=./storage/uploads
VECTOR_STORE_PATH=./storage/vector_store
```

### OPTIONAL (Add if needed)
```env
# Gmail Automation
GMAIL_EMAIL=your@gmail.com
GMAIL_APP_PASSWORD=16-char-password

# WhatsApp
***REMOVED***_ACCOUNT_SID=ACxxxx
***REMOVED***_***REMOVED***=token
***REMOVED***_WHATSAPP_FROM=whatsapp:+14155238886

# Push Notifications
ONESIGNAL_APP_ID=your-app-id
ONESIGNAL_REST_API_KEY=your-key
```

---

## 🎯 DEPLOYMENT STEPS

### Step 1: Create Render Web Service

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:

```
Name: regnova-backend
Region: Oregon (US West)
Branch: main
Runtime: Python 3
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

### Step 2: Add Environment Variables

Click **"Environment"** tab and add:

```
SECRET_KEY = [Generate new with: python -c "import secrets; print(secrets.token_urlsafe(32))"]
GEMINI_API_KEY = [Your Gemini API key]
DATABASE_URL = [Render provides this]
ENVIRONMENT = production
DEBUG = False
LLM_MODEL = gemini-1.5-pro
RAG_TOP_K = 10
RAG_RERANK = true
ENABLE_PROMPT_INJECTION_GUARD = true
ENABLE_HALLUCINATION_GUARD = true
```

### Step 3: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `regnova-db`
3. Plan: Free
4. Click **"Create Database"**
5. Copy **"Internal Database URL"**
6. Add to your web service as `DATABASE_URL`

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Your backend will be live at: `https://regnova-backend.onrender.com`

---

## 🌐 FRONTEND DEPLOYMENT (VERCEL)

### Step 1: Update Frontend Config

Update `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://regnova-backend.onrender.com
```

### Step 2: Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

Or use Vercel Dashboard:
1. Go to https://vercel.com
2. Import GitHub repo
3. Set Root Directory: `frontend`
4. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = `https://regnova-backend.onrender.com`
5. Deploy!

---

## ✅ VERIFICATION

### Test Backend
```bash
curl https://regnova-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Test Frontend
Visit: `https://your-app.vercel.app`

Should see landing page ✅

---

## 🐛 TROUBLESHOOTING

### Issue: "Application failed to respond"
**Solution:** Check logs in Render dashboard
- Most common: Missing environment variables
- Check DATABASE_URL is set
- Check GEMINI_API_KEY is valid

### Issue: Database connection error
**Solution:** 
- Ensure PostgreSQL created
- Copy Internal Database URL
- Add as DATABASE_URL in web service

### Issue: "Module not found"
**Solution:** 
- Check requirements.txt is complete
- Verify build command runs successfully

### Issue: CORS errors on frontend
**Solution:** Update backend CORS in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 DELIVERABLES CHECKLIST

### ✅ Deployment
- [ ] Backend deployed on Render
- [ ] Frontend deployed on Vercel
- [ ] Database connected
- [ ] Environment variables set
- [ ] Health check passing

### ✅ Features Working
- [ ] User registration/login
- [ ] PDF upload
- [ ] Chat with RAG
- [ ] Source citations
- [ ] Export JSON/PDF
- [ ] Prompt injection guard
- [ ] Hallucination detection

### ✅ Documentation
- [ ] README with setup instructions
- [ ] Architecture diagram
- [ ] Tech justification
- [ ] Security considerations
- [ ] User portal URL

---

## 🎯 URLS TO SUBMIT

After deployment, you'll have:

```
Backend API: https://regnova-backend.onrender.com
Frontend: https://regnova.vercel.app
GitHub: https://github.com/Khalid2703/Full-stack-PDF-knowledge-assistant
```

---

## ⏱️ TIMELINE

- **Hour 1:** Deploy backend to Render (30 min)
- **Hour 2:** Deploy frontend to Vercel (15 min)
- **Hour 3:** Test all features (30 min)
- **Hour 4:** Create documentation (45 min)

---

## 🆘 EMERGENCY CONTACTS

If stuck:
1. Check Render logs: Dashboard → Service → Logs
2. Check Vercel logs: Dashboard → Deployments → Logs
3. Test locally first: `npm run build`

---

**Ready to deploy! Follow steps 1-4 and you'll be live in 30 minutes!** 🚀
