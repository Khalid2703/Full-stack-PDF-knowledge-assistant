# Regnova - Full-Stack PDF Knowledge Assistant

A production-ready AI-powered knowledge assistant that enables users to upload PDFs, scrape web content, and interact with documents through an intelligent chat interface with RAG (Retrieval-Augmented Generation) capabilities.

## 🏗️ Project Structure

```
Regnova/
├── backend/          # FastAPI backend with RAG pipeline
│   ├── app/         # Application code
│   ├── Dockerfile   # Backend container configuration
│   └── requirements.txt
│
├── frontend/        # Next.js frontend
│   ├── src/        # Source code
│   ├── Dockerfile  # Frontend container configuration
│   └── package.json
│
└── docker-compose.yml  # Local development setup
```

## ✨ Features

- 📄 **PDF Upload & Processing** - Upload and process PDF documents with OCR support
- 🌐 **Web Scraping** - Extract content from URLs
- 🔍 **Semantic Search** - Vector-based search using FAISS
- 🤖 **AI Chat Interface** - RAG-powered Q&A with source citations
- 🔐 **JWT Authentication** - Secure user authentication
- 📊 **File Management** - Upload, view, and delete documents
- 🎯 **Smart Citations** - Automatic source referencing in responses

## 🚀 Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- SQLite/PostgreSQL
- FAISS (Vector Search)
- Google Gemini API
- Tesseract OCR

**Frontend:**
- Next.js 14
- TypeScript
- Tailwind CSS
- React Query

## 📦 Deployment on Render

This application is deployed on Render with separate services for backend and frontend. See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## 🔧 Local Development

See individual README files:
- [Backend Setup](./backend/README.md)
- [Frontend Setup](./frontend/README.md)

## 📝 License

MIT License

