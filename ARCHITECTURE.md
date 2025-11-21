# 🏗️ REGNOVA ARCHITECTURE DOCUMENT

## 📊 SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                    (Next.js 14 + React 18)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Login   │  │  Upload  │  │   Chat   │  │ Profile  │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                              │
│                     (FastAPI Backend)                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │   Auth   │  │  Upload  │  │   Chat   │  │Automation│          │
│  │ Routes   │  │ Routes   │  │ Routes   │  │ Routes   │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼─────────────┼─────────────┼──────────────┼────────────────┘
        │             │             │              │
        ▼             ▼             ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ Auth Service │  │ PDF Service  │  │ Chat Service │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ RAG Pipeline │  │  Embeddings  │  │  Reranking   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────┬──────────────────────┬───────────────────┬────────────────────┘
     │                      │                   │
     ▼                      ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AI & ML LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              Google Gemini API (LLM)                     │      │
│  │  • Answer Generation                                     │      │
│  │  • Prompt Safety Check                                   │      │
│  │  • Hallucination Detection                              │      │
│  └──────────────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │         Sentence Transformers (Embeddings)               │      │
│  │  • Document Chunking                                     │      │
│  │  • Vector Generation                                     │      │
│  │  • Semantic Search                                       │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
     │                      │                   │
     ▼                      ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ PostgreSQL   │  │ FAISS Vector │  │ File Storage │            │
│  │   Database   │  │    Store     │  │   System     │            │
│  │              │  │              │  │              │            │
│  │ • Users      │  │ • Embeddings │  │ • PDF Files  │            │
│  │ • Files      │  │ • Chunks     │  │ • Uploads    │            │
│  │ • Chats      │  │ • Index      │  │              │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 RAG DATA FLOW

```
USER QUERY
    │
    ▼
┌─────────────────┐
│ 1. Query Input  │ ← User asks question
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Safety Check │ ← Prompt injection detection
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Embedding    │ ← Convert query to vector
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Vector Search│ ← Search FAISS index
│   (FAISS)       │   Top-K similar chunks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Reranking    │ ← Cross-encoder scoring
│   (Optional)    │   Relevance boost
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Context Build│ ← Combine top chunks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. LLM Generate │ ← Gemini generates answer
│   (Gemini)      │   With context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 8. Citation     │ ← Add source references
│   Engine        │   [Source N] format
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 9. Safety Check │ ← Hallucination detection
│   (Validation)  │   Verify against sources
└────────┬────────┘
         │
         ▼
    RESPONSE TO USER
    with citations
```

---

## 🛡️ SECURITY ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: AUTHENTICATION                                    │
│  ┌────────────────────────────────────────┐                │
│  │ • JWT Token-based auth                 │                │
│  │ • Password hashing (bcrypt)            │                │
│  │ • Token expiration (30 min)            │                │
│  │ • Secure token storage                 │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  Layer 2: API SECURITY                                      │
│  ┌────────────────────────────────────────┐                │
│  │ • CORS configuration                   │                │
│  │ • Rate limiting (10 req/min)           │                │
│  │ • Request validation                   │                │
│  │ • HTTPS only                           │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  Layer 3: AI SAFETY                                         │
│  ┌────────────────────────────────────────┐                │
│  │ • Prompt injection detection           │                │
│  │ • Hallucination guard                  │                │
│  │ • Content filtering                    │                │
│  │ • Source verification                  │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  Layer 4: DATA SECURITY                                     │
│  ┌────────────────────────────────────────┐                │
│  │ • Encrypted connections (TLS)          │                │
│  │ • Secure env variables                 │                │
│  │ • User data isolation                  │                │
│  │ • File upload validation               │                │
│  └────────────────────────────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 TECHNOLOGY STACK

### Frontend
- **Framework:** Next.js 14 (React 18)
- **Styling:** Tailwind CSS + ShadCN UI
- **State:** Zustand
- **HTTP:** Axios
- **Validation:** Zod + React Hook Form
- **Export:** jsPDF

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Auth:** JWT (python-jose)
- **Database:** PostgreSQL + SQLAlchemy
- **AI/ML:**
  - Google Gemini API (LLM)
  - Sentence Transformers (Embeddings)
  - FAISS (Vector Store)
- **PDF:** PyMuPDF + Tesseract OCR
- **Web:** BeautifulSoup + Requests

### DevOps
- **Containerization:** Docker
- **Backend Hosting:** Render
- **Frontend Hosting:** Vercel
- **Database:** Render PostgreSQL
- **CI/CD:** GitHub Actions
- **Monitoring:** Loguru

---

## 🔄 COMPONENT INTERACTION

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│          │  HTTPS  │          │  SQL    │          │
│ Frontend ├────────►│ Backend  ├────────►│ Database │
│          │         │          │         │          │
└──────────┘         └─────┬────┘         └──────────┘
                           │
                           │ API Calls
                           ▼
                     ┌──────────┐
                     │          │
                     │  Gemini  │
                     │   API    │
                     │          │
                     └──────────┘
                           │
                           │ Embeddings
                           ▼
                     ┌──────────┐
                     │          │
                     │  FAISS   │
                     │  Vector  │
                     │  Store   │
                     │          │
                     └──────────┘
```

---

## 📈 PERFORMANCE OPTIMIZATION

### PDF Processing: < 30 seconds
- **Parallel processing** for multi-page PDFs
- **Cached** text extraction results
- **Progressive** chunking during upload

### Vector Search: < 2 seconds
- **FAISS** indexing for O(log n) search
- **In-memory** vector storage
- **Batch** embedding generation

### API Response: < 3 seconds
- **Connection pooling** for database
- **Caching** for repeated queries
- **Async I/O** for concurrent requests

---

## 🎯 SCALABILITY CONSIDERATIONS

### Horizontal Scaling
- Stateless API design
- Database connection pooling
- Load balancer ready

### Vertical Scaling
- Efficient memory management
- Optimized vector operations
- Batched processing

---

This architecture ensures:
✅ High performance (< 30s PDF processing)
✅ Security at every layer
✅ Scalable design
✅ Production-ready deployment
✅ AI safety guarantees
