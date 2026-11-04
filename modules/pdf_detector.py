"""
pdf_detector.py – Detect whether a PDF is text-based or image-based (scanned).
"""
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def detect_pdf_type(pdf_path: str) -> Tuple[str, float]:
    """
    Detect whether a PDF page is text-based or image-based.

    Returns:
        (pdf_type, text_ratio) where pdf_type is 'text' or 'image'
        and text_ratio is the fraction of pages that have extractable text.
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            return "unknown", 0.0

        text_pages = 0
        for page in doc:
            text = page.get_text("text").strip()
            if len(text) > 50:          # more than 50 chars → text-based page
                text_pages += 1
        doc.close()

        ratio = text_pages / total_pages
        pdf_type = "text" if ratio >= 0.5 else "image"
        logger.info("PDF type detected: %s (text ratio=%.2f)", pdf_type, ratio)
        return pdf_type, ratio

    except Exception as exc:
        logger.error("PDF type detection failed: %s", exc)
        return "text", 0.0          # default to text extraction


def is_password_protected(pdf_path: str) -> bool:
    """Return True if the PDF requires a password to open."""
    try:
        import fitz

        doc = fitz.open(pdf_path)
        protected = doc.is_encrypted
        if protected:
            # Try without password
            authenticated = doc.authenticate("")
            protected = authenticated == 0
        doc.close()
        return protected
    except Exception:
        return False


def get_pdf_page_count(pdf_path: str) -> int:
    """Return the number of pages in a PDF."""
    try:
        import fitz

        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 0
