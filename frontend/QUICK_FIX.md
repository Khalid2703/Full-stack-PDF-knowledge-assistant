# 🚀 QUICK FIX GUIDE - REGNOVA

## ⚡ 3-MINUTE FIX

### If Chat Not Working:

```bash
# 1. Install missing packages
cd C:\Users\hp\Regnova\frontend
npm install @radix-ui/react-slot

# 2. Restart
npm run dev
```

### If Backend Connection Error:

```bash
# Check backend is running
cd C:\Users\hp\Regnova\backend
python -m app.main
```

### If Login Not Working:

```bash
# Check .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📋 CHECKLIST

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Logged in successfully
- [ ] Uploaded at least one PDF
- [ ] Can see files in dashboard
- [ ] Chat responds to questions

---

## 🎯 DAY 3 STATUS

**Overall: 85% Complete**

✅ Authentication - DONE
✅ File Upload - DONE  
✅ Chat Interface - DONE (Fixed)
✅ Dashboard - DONE
✅ Profile - DONE
❌ SSE Streaming - TODO
❌ Deployment - TODO

---

## 🐛 COMMON ERRORS

### Error: "Module not found"
```bash
npm install [missing-package]
```

### Error: "Connection refused"
Check backend is running

### Error: "Unauthorized"
Login again

---

## 📞 NEED HELP?

1. Share terminal error text
2. Share browser console error (F12)
3. I'll fix immediately!

---

**Updated: 2025-11-20**
**Status: Ready for Testing**
