"""
ocr_engine.py – OCR extraction for image-based / scanned PDFs using Tesseract + OpenCV.
"""
import logging
import tempfile
import os
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

# Tesseract path for Windows (default installation)
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Tirth\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
    "tesseract",  # if on PATH
]


def configure_tesseract():
    """Configure pytesseract to use the correct Tesseract executable."""
    try:
        import pytesseract

        for path in TESSERACT_PATHS:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info("Tesseract found at: %s", path)
                return True
        logger.warning("Tesseract executable not found in common paths. OCR may fail.")
        return False
    except ImportError:
        logger.error("pytesseract not installed.")
        return False


def preprocess_image_for_ocr(image_array) -> object:
    """
    Apply OpenCV preprocessing to improve OCR accuracy.
    Steps: grayscale → denoise → thresholding → deskew.
    """
    try:
        import cv2
        import numpy as np

        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Slight deskew
        coords = np.column_stack(np.where(thresh < 128))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = 90 + angle
            if abs(angle) > 0.5:
                (h, w) = thresh.shape
                M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
                thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return thresh
    except Exception as exc:
        logger.error("Image preprocessing failed: %s", exc)
        return image_array


def pdf_page_to_image(pdf_path: str, page_num: int, dpi: int = 300):
    """Convert a PDF page to a numpy image array using PyMuPDF."""
    try:
        import fitz
        import numpy as np

        doc = fitz.open(pdf_path)
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        doc.close()

        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:  # RGBA → RGB
            import cv2
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        return img_array
    except Exception as exc:
        logger.error("PDF to image conversion failed on page %d: %s", page_num, exc)
        return None


def ocr_page(pdf_path: str, page_num: int, lang: str = "eng") -> str:
    """
    Run OCR on a single PDF page.
    Returns extracted text string.
    """
    configure_tesseract()
    try:
        import pytesseract

        img = pdf_page_to_image(pdf_path, page_num)
        if img is None:
            return ""

        processed = preprocess_image_for_ocr(img)

        # OCR config optimised for bank statements
        config = "--oem 3 --psm 6 -c preserve_interword_spaces=1"
        text = pytesseract.image_to_string(processed, lang=lang, config=config)
        return text
    except Exception as exc:
        logger.error("OCR failed on page %d: %s", page_num, exc)
        return ""


def ocr_pdf(pdf_path: str, lang: str = "eng") -> List[str]:
    """
    Run OCR on all pages of a PDF.
    Returns a list of text strings, one per page.
    """
    pages_text = []
    try:
        import fitz

        doc = fitz.open(pdf_path)
        total = len(doc)
        doc.close()

        for i in range(total):
            logger.info("OCR page %d/%d", i + 1, total)
            text = ocr_page(pdf_path, i, lang)
            pages_text.append(text)
    except Exception as exc:
        logger.error("OCR PDF failed: %s", exc)
    return pages_text


def is_tesseract_available() -> bool:
    """Check whether Tesseract OCR is available on this system."""
    configure_tesseract()
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
