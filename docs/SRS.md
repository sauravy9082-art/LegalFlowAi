# Software Requirements Specification (SRS) - LegalFlow AI

## 1. Introduction
LegalFlow AI is a privacy-first, offline-capable AI legal document assistant, contract redliner, and drafting platform designed for B.Tech/B.Sc. IT final-year project standards.

### 1.1 Purpose
LegalFlow AI assists users (tenants, freelancers, students, small business owners) in understanding complex contracts, detecting risky clauses, generating redlined counter-proposals, drafting agreements, and asking document-specific questions without sending sensitive contract data to cloud servers.

### 1.2 Scope
- **Offline Local AI Execution**: Integrates with local Ollama instances running open-source LLMs (Qwen2, Llama3, Mistral).
- **Dual Text Extraction & OCR**: PyMuPDF direct page/layout extraction + Tesseract OCR fallback for scanned contracts & images.
- **Deterministic Contract Safety Score**: Mathematical 0-100 risk scoring algorithm.
- **Visual Bounding Box Highlighting**: Highlights flagged risky clauses directly in the PDF viewer canvas.
- **Multilingual Support**: English, Hindi, and Marathi explanations.
- **Contract Redlining**: Native DOCX counter-proposal generation with tracked deletions and green replacements.
- **Template Drafting**: Customized agreement generator for NDA, Lease, Freelance contracts.

---

## 2. Functional Requirements

### FR-1: User Authentication & Security
- Secure registration and login using JWT tokens and bcrypt password hashing.

### FR-2: Document Ingestion & Extraction
- Support PDF, DOCX, TXT, PNG, JPG files.
- Automatically detect scanned documents and trigger Tesseract OCR.

### FR-3: Local AI & Structured Legal Analysis
- Extract summary, financial obligations, notice deadlines, and clause categories.
- Ensure 100% structured Pydantic JSON parsing with corrective retry handling.

### FR-4: Visual PDF Risk Citation Overlay
- Map flagged clause text to normalized page coordinates `(x0, y0, x1, y1)`.
- Render semi-transparent color overlays over PDF pages.

### FR-5: Contract Redlining Engine
- Generate tracked DOCX counter-proposal with red strikethrough and green underlines.

### FR-6: Multilingual Legal Explanation
- Preserve original English contract clause while displaying explanations in English, Hindi, or Marathi.

---

## 3. Non-Functional Requirements
- **Privacy First**: Zero external API uploads.
- **Offline Capability**: Operates fully on local host without active internet.
- **Performance**: Response times < 3s for text extraction, < 10s for local Ollama inference.
