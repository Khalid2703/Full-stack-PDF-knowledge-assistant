#!/bin/bash

echo "🔧 Committing Vercel deployment fixes..."
echo ""

cd "C:/Users/hp/Regnova"

# Add all modified files
git add frontend/next.config.js
git add frontend/.env.production
git add frontend/tailwind.config.js
git add frontend/vercel.json
git add frontend/.gitignore
git add frontend/postcss.config.js
git add frontend/VERCEL_DEPLOYMENT_FIX.md

echo "✅ Files staged"
echo ""

# Commit with detailed message
git commit -m "Fix: Vercel deployment - CSS & Auth issues resolved

- Remove output: standalone from next.config.js (breaks CSS)
- Add correct .env.production with backend URL
- Enhance tailwind.config.js content paths
- Clean up vercel.json (remove problematic config)
- Add .gitignore for proper env file handling
- Add comprehensive deployment documentation"

echo ""
echo "✅ Changes committed"
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ DONE! Changes pushed to GitHub"
echo ""
echo "🎯 Next steps:"
echo "1. Go to Vercel dashboard"
echo "2. Your deployment will auto-trigger"
echo "3. Wait for build to complete (2-3 minutes)"
echo "4. Check your live site!"
echo ""
echo "📋 If needed, add environment variable in Vercel:"
echo "   Key: NEXT_PUBLIC_API_URL"
echo "   Value: https://regnova-backend-bs3v.onrender.com"
