#!/bin/bash

# Quick fix deployment script

echo "🔧 Committing reranking service fix..."
git add .
git commit -m "Fix: Replace CrossEncoder with Gemini-based reranking (removes sentence-transformers dependency)"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Done! Render will auto-deploy the fix."
echo ""
echo "Monitor deployment at: https://dashboard.render.com"
