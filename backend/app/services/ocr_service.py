import shutil
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.tesseract_cmd = shutil.which("tesseract")

    def is_tesseract_available(self) -> bool:
        return self.tesseract_cmd is not None

    async def ocr_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Perform OCR on an image file (Rule 15).
        Returns NOT VERIFIED / error structure if Tesseract is not installed on local machine.
        """
        if not self.is_tesseract_available():
            logger.warning("OCR requested but Tesseract binary is not installed in PATH.")
            return [{
                "page_number": 1,
                "text": "[NOT VERIFIED — Tesseract executable is unavailable on host system.]",
                "width": 612.0,
                "height": 792.0,
                "words": []
            }]

        try:
            import pytesseract
            from PIL import Image

            img = Image.open(image_path)
            width, height = img.size
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            words = []
            extracted_text = []
            n_boxes = len(ocr_data["text"])
            for i in range(n_boxes):
                word_text = ocr_data["text"][i].strip()
                if word_text:
                    extracted_text.append(word_text)
                    words.append({
                        "xmin": float(ocr_data["left"][i]),
                        "ymin": float(ocr_data["top"][i]),
                        "xmax": float(ocr_data["left"][i] + ocr_data["width"][i]),
                        "ymax": float(ocr_data["top"][i] + ocr_data["height"][i]),
                        "word": word_text,
                        "confidence": float(ocr_data["conf"][i])
                    })

            return [{
                "page_number": 1,
                "text": " ".join(extracted_text),
                "width": float(width),
                "height": float(height),
                "words": words
            }]
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return [{
                "page_number": 1,
                "text": f"[OCR Failed: {e}]",
                "width": 612.0,
                "height": 792.0,
                "words": []
            }]

    async def ocr_pdf_page(self, fitz_page) -> Optional[Dict[str, Any]]:
        if not self.is_tesseract_available():
            return None

        try:
            import pytesseract
            from PIL import Image
            import io

            pix = fitz_page.get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes()))
            width, height = img.size
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

            words = []
            extracted_text = []
            n_boxes = len(ocr_data["text"])
            for i in range(n_boxes):
                word_text = ocr_data["text"][i].strip()
                if word_text:
                    extracted_text.append(word_text)
                    words.append({
                        "xmin": float(ocr_data["left"][i]),
                        "ymin": float(ocr_data["top"][i]),
                        "xmax": float(ocr_data["left"][i] + ocr_data["width"][i]),
                        "ymax": float(ocr_data["top"][i] + ocr_data["height"][i]),
                        "word": word_text,
                        "confidence": float(ocr_data["conf"][i])
                    })

            return {
                "text": " ".join(extracted_text),
                "width": float(width),
                "height": float(height),
                "words": words
            }
        except Exception as e:
            logger.error(f"PDF Page OCR failed: {e}")
            return None
