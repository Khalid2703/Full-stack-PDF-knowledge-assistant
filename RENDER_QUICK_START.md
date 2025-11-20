# 🚀 Quick Start: Deploy to Render

## 📝 Pre-Deployment Checklist

- [ ] Git repository initialized
- [ ] All changes committed
- [ ] README.md in root folder
- [ ] .gitignore configured
- [ ] Gemini API key ready

## 🔥 Quick Deploy Steps

### 1️⃣ Push to GitHub

```bash
# From project root
git init
git add .
git commit -m "Initial commit: Regnova Knowledge Assistant"
git branch -M main
git remote add origin https://github.com/Khalid2703/Full-stack-PDF-knowledge-assistant.git
git push -u origin main
```

### 2️⃣ Deploy Backend (5 minutes)

1. **Render Dashboard** → **"New +"** → **"Web Service"**
2. Connect repo: `Full-stack-PDF-knowledge-assistant`
3. Configure:
   - **Name:** `regnova-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `Dockerfile` (it's in backend folder)
4. **Environment Variables:**
   ```
   DATABASE_URL=sqlite:///./regnova.db
   SECRET_KEY=change-this-to-random-string
   GEMINI_API_KEY=your-gemini-api-key
   ENVIRONMENT=production
   PORT=8000
   ```
5. **Mount Disk:**
   - Name: `regnova-storage`
   - Mount: `/app/storage`
   - Size: 1GB
6. **Deploy!** ✅

**Save backend URL:** `https://your-backend.onrender.com`

### 3️⃣ Deploy Frontend (5 minutes)

1. **Render Dashboard** → **"New +"** → **"Web Service"**
2. Same repo: `Full-stack-PDF-knowledge-assistant`
3. Configure:
   - **Name:** `regnova-frontend`
   - **Root Directory:** `frontend`
   - **Runtime:** `Docker`
   - **Dockerfile Path:** `Dockerfile`
4. **Environment Variables:**
   ```
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```
   ⚠️ **Replace** `your-backend.onrender.com` with actual backend URL!
5. **Deploy!** ✅

### 4️⃣ Update Backend CORS

1. Go to **backend service** → **Environment**
2. Add:
   ```
   CORS_ORIGINS=https://your-frontend.onrender.com
   ```
   ⚠️ **Replace** `your-frontend.onrender.com` with actual frontend URL!
3. **Manual Deploy** (trigger redeploy)

### 5️⃣ Test! 🎉

Visit your frontend URL and:
- ✅ Register/Login
- ✅ Upload PDF
- ✅ Ask questions

## 🐛 Common Issues

**Build fails:**
- Check logs in Render dashboard
- Verify Dockerfile paths
- Ensure requirements.txt/package.json exist

**Frontend can't connect:**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend service is running
- Update CORS_ORIGINS in backend

**Files not persisting:**
- Ensure disk is mounted at `/app/storage`
- Check disk size (increase if full)

## 📊 After Deployment

- **Backend:** `https://your-backend.onrender.com/api/docs`
- **Frontend:** `https://your-frontend.onrender.com`
- **Logs:** Available in Render dashboard
- **Metrics:** CPU, Memory, Requests

## 💡 Pro Tips

1. **Free Tier:** Services spin down after 15min inactivity (cold start ~30s)
2. **Paid Tier:** Always-on, faster cold starts
3. **PostgreSQL:** Consider upgrading to PostgreSQL for production
4. **Monitoring:** Set up email alerts for service failures

---

**Done!** Your app is live! 🚀

