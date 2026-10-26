# Viva Voce Q&A Preparation Guide - LegalFlow AI

## Q1: What makes LegalFlow AI different from online legal chatbots like ChatGPT?
**Answer**: LegalFlow AI is 100% privacy-first and operates offline using local Ollama LLM models. Sensitive contracts are never uploaded to third-party cloud servers. Furthermore, LegalFlow AI provides visual bounding-box PDF risk highlighting, deterministic safety scoring (0-100), multilingual explanations (Hindi, Marathi), and native DOCX redline counter-proposal generation.

## Q2: How does the system highlight exact clause bounding boxes in scanned PDFs?
**Answer**: The system uses PyMuPDF layout word extraction or Tesseract OCR image data to map word bounding boxes `(x0, y0, x1, y1)`. These coordinates are normalized into percentage values and passed to the frontend React PDF viewer canvas, which renders semi-transparent risk overlays.

## Q3: Is the Contract Safety Score generated randomly by the LLM?
**Answer**: No. LegalFlow AI uses a deterministic mathematical risk scoring engine. Base score starts at 100 and points are deducted based on identifiable risk patterns: Critical Risks (-20 pts), High Concerns (-12 pts), and Warnings (-5 pts). This guarantees repeatable, verifiable results.

## Q4: How is Multilingual Support implemented without replacing original contract text?
**Answer**: The original legal clause is strictly preserved in its native English format. The `MultilingualExplanationService` generates parallel explanations in Hindi or Marathi based on legal terminology dictionaries and Ollama translation prompts, allowing users to understand the clause in their local language without altering the legal text.

## Q5: How does the Redlining feature work?
**Answer**: The `RedlineEngine` parses flagged risky clauses, generates safer counter-proposals, and uses `python-docx` to build a Word document with red strikethrough for deleted text (`font.strike = True`) and green underline for proposed terms (`font.underline = True`).
