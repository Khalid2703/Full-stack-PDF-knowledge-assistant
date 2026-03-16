

# Regnova – Full-Stack PDF Knowledge Assistant

**Regnova** is a production-ready AI-powered knowledge assistant that enables users to upload PDFs, scrape web content, and interact with documents through an intelligent chat interface.
It leverages **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware responses grounded in the uploaded content.

---

# 🏗️ Project Structure

```
Regnova/
├── backend/                # FastAPI backend implementing the RAG pipeline
│   ├── app/                # Core backend application code
│   ├── Dockerfile          # Backend container configuration
│   └── requirements.txt
│
├── frontend/               # Next.js frontend application
│   ├── src/                # Frontend source code
│   ├── Dockerfile          # Frontend container configuration
│   └── package.json
│
└── docker-compose.yml      # Local development orchestration
```

---

# ✨ Features

* **📄 PDF Upload & Processing**
  Upload and process PDF documents with OCR support for scanned files.

* **🌐 Web Content Ingestion**
  Extract and index content from external URLs.

* **🔍 Semantic Search**
  Perform vector-based similarity search using **FAISS**.

* **🤖 AI Chat Interface**
  Query documents through an intelligent chat system powered by **RAG**.

* **🔐 Secure Authentication**
  JWT-based authentication for secure user access.

* **📊 File Management**
  Upload, view, and manage document collections.

* **🎯 Smart Citations**
  Automatically reference source documents in generated responses.

---

# 🚀 Tech Stack

### Backend

* **FastAPI** (Python 3.11)
* **FAISS** for vector search
* **SQLite / PostgreSQL**
* **Google Gemini API**
* **Tesseract OCR**

### Frontend

* **Next.js 14**
* **TypeScript**
* **Tailwind CSS**
* **React Query**

---

# 📦 Deployment

The application can be deployed using **Render** with separate services for the backend and frontend.

See **`DEPLOYMENT.md`** for detailed deployment instructions.

---

# 🔧 Local Development

For local setup instructions, refer to:

* **Backend Setup**
* **Frontend Setup**

Both services can be run locally using **Docker Compose**.

---

# 📄 License

This project is licensed under the **MIT License**.

---

✅ This version:

* Looks **more professional**
* Uses **cleaner GitHub formatting**
* Sounds **more production-grade**
* Makes the project look **stronger for hiring managers**

