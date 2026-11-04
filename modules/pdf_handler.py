"""
pdf_handler.py – Handle PDF file operations: validation, loading, password handling.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".pdf"}


def validate_pdf(file_path: str) -> Tuple[bool, str]:
    """
    Validate a PDF file.

    Returns:
        (is_valid, error_message) – error_message is empty if valid.
    """
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type '{path.suffix}'. Only PDF files are supported."

    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size {file_size_mb:.1f} MB exceeds the {MAX_FILE_SIZE_MB} MB limit."

    # Try to open with PyMuPDF
    try:
        import fitz

        doc = fitz.open(file_path)
        if doc.is_encrypted:
            authenticated = doc.authenticate("")
            if authenticated == 0:
                doc.close()
                return False, "PDF is password-protected. Please provide the password or use an unprotected version."
        if len(doc) == 0:
            doc.close()
            return False, "PDF appears to be empty (no pages found)."
        doc.close()
    except Exception as exc:
        return False, f"Cannot open PDF – it may be corrupted or malformed. Error: {exc}"

    return True, ""


def open_pdf_with_password(file_path: str, password: str) -> Tuple[bool, str]:
    """
    Attempt to open a password-protected PDF.

    Returns:
        (success, error_message)
    """
    try:
        import fitz

        doc = fitz.open(file_path)
        if doc.is_encrypted:
            result = doc.authenticate(password)
            doc.close()
            if result == 0:
                return False, "Incorrect password."
            return True, ""
        doc.close()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def get_file_info(file_path: str) -> dict:
    """Return basic metadata about a PDF file."""
    path = Path(file_path)
    info = {
        "filename": path.name,
        "size_bytes": 0,
        "size_mb": 0.0,
        "pages": 0,
        "is_encrypted": False,
    }
    if not path.exists():
        return info

    info["size_bytes"] = path.stat().st_size
    info["size_mb"] = info["size_bytes"] / (1024 * 1024)

    try:
        import fitz

        doc = fitz.open(file_path)
        info["pages"] = len(doc)
        info["is_encrypted"] = doc.is_encrypted
        doc.close()
    except Exception:
        pass

    return info
