import fitz  # PyMuPDF
import os
import logging
from typing import List, Dict, Any
from app.services.ocr_service import OCRService

logger = logging.getLogger(__name__)

class PDFParserService:
    def __init__(self):
        self.ocr_service = OCRService()

    async def extract_text_and_coords(self, file_path: str, original_filename: str) -> List[Dict[str, Any]]:
        """
        Extract page text, blocks, words, and bounding coordinates (xmin, ymin, xmax, ymax) using PyMuPDF (fitz).
        Falls back to OCR only if extracted text is empty/insufficient (Rule 15).
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".docx":
            return await self._extract_docx(file_path)
        elif ext == ".txt":
            return await self._extract_txt(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            return await self.ocr_service.ocr_image(file_path)

        # PDF Processing
        pages_data = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                page_width = float(rect.width)
                page_height = float(rect.height)
                text = page.get_text("text")

                # Extract word-level bounding boxes (x0, y0, x1, y1, word, block_no, line_no, word_no)
                words = page.get_text("words")
                word_boxes = []
                for w in words:
                    word_boxes.append({
                        "xmin": float(w[0]),
                        "ymin": float(w[1]),
                        "xmax": float(w[2]),
                        "ymax": float(w[3]),
                        "word": w[4],
                        "block_no": w[5],
                        "line_no": w[6]
                    })

                # Check if text is sufficient (Rule 15)
                if len(text.strip()) < 30 and self.ocr_service.is_tesseract_available():
                    logger.info(f"Page {page_num + 1} has insufficient vector text ({len(text.strip())} chars). Applying Tesseract OCR.")
                    ocr_result = await self.ocr_service.ocr_pdf_page(page)
                    if ocr_result and len(ocr_result.get("text", "").strip()) > len(text.strip()):
                        text = ocr_result["text"]
                        word_boxes = ocr_result.get("words", [])

                pages_data.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "width": page_width,
                    "height": page_height,
                    "words": word_boxes
                })
            doc.close()
        except Exception as e:
            logger.error(f"PyMuPDF PDF parsing error for '{file_path}': {e}")
            # If PDF opening failed, attempt image OCR fallback if possible
            raise RuntimeError(f"Failed to parse PDF document: {e}")

        return pages_data

    async def _extract_docx(self, file_path: str) -> List[Dict[str, Any]]:
        import docx
        doc = docx.Document(file_path)
        full_text = []
        for p in doc.paragraphs:
            if p.text.strip():
                full_text.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    full_text.append(" | ".join(row_text))
        
        combined = "\n".join(full_text)
        return [{
            "page_number": 1,
            "text": combined,
            "width": 612.0,
            "height": 792.0,
            "words": []
        }]

    async def _extract_txt(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [{
            "page_number": 1,
            "text": text,
            "width": 612.0,
            "height": 792.0,
            "words": []
        }]
