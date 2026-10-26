# System Architecture - LegalFlow AI

## 1. High-Level Component Diagram

```
+-----------------------------------------------------------------------------------+
|                                 FRONTEND (React + Vite + Tailwind)                |
|  +-------------------+  +--------------------+  +------------------+  +------------+  |
|  | Split-Screen PDF  |  | Risk Sidebar &     |  | Multilingual Chat|  | Redline &  |  |
|  | Viewer (PDF.js)   |  | Safety Score (0-100|  | & Timeline View  |  | Template UI|  |
+--+-------------------+--+--------------------+--+------------------+--+------------+--+
                                        |  REST API / SSE
                                        v
+-----------------------------------------------------------------------------------+
|                                 BACKEND (FastAPI + Pydantic)                      |
|  +-------------------+  +--------------------+  +------------------+  +------------+  |
|  | Document & OCR    |  | AI Provider Engine |  | Risk & Redline   |  | Template & |  |
|  | Pipeline (PyMuPDF)|  | (Ollama + Structured| | Engine (Docx)    |  | Compare    |  |
+--+-------------------+--+--------------------+--+------------------+--+------------+--+
            |                          |                          |
            v                          v                          v
+-----------------------+  +-----------------------+  +-----------------------+
|  Local Storage / DB   |  | Local Ollama Instance |  | Local RAG Engine      |
|  (SQLite + SQLAlchemy)|  | (Qwen/Llama3/Mistral) |  | (ChromaDB + Sentence) |
+-----------------------+  +-----------------------+  +-----------------------+
```

## 2. Layer Description
- **Frontend Layer**: Built with React 18, Vite, Tailwind CSS, Lucide icons, and Axios. Features responsive split-screen viewing and visual risk overlays.
- **API Layer**: FastAPI backend with Pydantic schemas, JWT authentication, background processing, and CORS security.
- **AI Abstraction Layer**: `OllamaProvider` connecting to `http://localhost:11434` with structured JSON parsing & markdown code block cleaner.
- **Extraction Layer**: PyMuPDF for vector PDFs and Tesseract OCR for scanned images/PDFs.
- **Storage Layer**: SQLite relational database with SQLAlchemy ORM and local filesystem storage for uploaded and generated `.docx` files.
