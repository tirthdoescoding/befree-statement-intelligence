"""
bank_parser.py – High-level orchestration: detect PDF type, extract text/OCR,
extract account info, parse transactions, deduplicate.
"""
import logging
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd

from modules.pdf_detector import detect_pdf_type, is_password_protected
from modules.text_extractor import extract_text_from_pdf, extract_tables_from_pdf, extract_account_info
from modules.transaction_parser import (
    parse_transactions_from_text,
    parse_transactions_from_table,
    deduplicate_transactions,
    normalize_transactions,
)

logger = logging.getLogger(__name__)


def process_pdf(
    pdf_path: str,
    password: Optional[str] = None,
    progress_callback=None,
) -> Dict:
    """
    Main entry point: process a bank statement PDF end-to-end.

    Returns a dict:
        {
            "account_info": dict,
            "transactions": pd.DataFrame,
            "pdf_type": str,
            "pages": int,
            "warnings": list[str],
            "errors": list[str],
        }
    """
    result = {
        "account_info": {},
        "transactions": pd.DataFrame(),
        "pdf_type": "unknown",
        "pages": 0,
        "warnings": [],
        "errors": [],
    }

    def _progress(step: str, pct: int):
        if progress_callback:
            progress_callback(step, pct)

    # --- Step 1: Password check ---
    _progress("Checking PDF protection...", 5)
    if is_password_protected(pdf_path):
        if not password:
            result["errors"].append("PDF is password-protected. Please provide the password.")
            return result
        # Try to authenticate (we pass through; pdfplumber/fitz will use env or ignore)
        logger.info("Password-protected PDF; attempting authentication.")

    # --- Step 2: Detect PDF type ---
    _progress("Detecting PDF type...", 15)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        if doc.is_encrypted and password:
            doc.authenticate(password)
        result["pages"] = len(doc)
        doc.close()
    except Exception as exc:
        result["errors"].append(f"Cannot open PDF: {exc}")
        return result

    pdf_type, text_ratio = detect_pdf_type(pdf_path)
    result["pdf_type"] = pdf_type

    # --- Step 3: Extract text ---
    _progress("Extracting text...", 30)
    pages_text = []
    all_tables = []

    if pdf_type == "text":
        try:
            pages_text = extract_text_from_pdf(pdf_path)
            all_tables = extract_tables_from_pdf(pdf_path)
        except Exception as exc:
            result["warnings"].append(f"Text extraction partially failed: {exc}")
    else:
        # OCR path
        _progress("Running OCR (this may take a moment)...", 40)
        try:
            from modules.ocr_engine import ocr_pdf, is_tesseract_available
            if is_tesseract_available():
                pages_text = ocr_pdf(pdf_path)
            else:
                result["warnings"].append(
                    "Tesseract OCR is not installed. Install it from https://github.com/UB-Mannheim/tesseract/wiki "
                    "and add it to PATH. Attempting text extraction as fallback."
                )
                pages_text = extract_text_from_pdf(pdf_path)
                all_tables = extract_tables_from_pdf(pdf_path)
        except Exception as exc:
            result["warnings"].append(f"OCR failed: {exc}. Falling back to text extraction.")
            pages_text = extract_text_from_pdf(pdf_path)
            all_tables = extract_tables_from_pdf(pdf_path)

    if not any(pages_text):
        result["warnings"].append("No text could be extracted from this PDF.")

    # --- Step 4: Extract account info ---
    _progress("Extracting account information...", 50)
    combined_text = "\n".join(pages_text)
    result["account_info"] = extract_account_info(combined_text)

    # --- Step 5: Parse transactions ---
    _progress("Parsing transactions...", 65)
    transactions = []

    # Try table extraction first (more structured)
    if all_tables:
        table_txns = parse_transactions_from_table(all_tables)
        if table_txns:
            transactions = table_txns
            logger.info("Parsed %d transactions from tables.", len(transactions))

    # Fall back to text parsing if tables yield nothing
    if not transactions and pages_text:
        text_txns = parse_transactions_from_text(pages_text)
        if text_txns:
            transactions = text_txns
            logger.info("Parsed %d transactions from text.", len(transactions))

    # --- Step 6: Deduplicate ---
    _progress("Deduplicating transactions...", 75)
    transactions = deduplicate_transactions(transactions)

    # --- Step 7: Normalise ---
    _progress("Normalising data...", 85)
    df = normalize_transactions(transactions)

    if df.empty:
        result["warnings"].append(
            "No transactions could be extracted. The statement format may not be supported yet."
        )

    result["transactions"] = df
    _progress("Done!", 100)
    return result


def process_multiple_pdfs(pdf_paths: List[str], progress_callback=None) -> List[Dict]:
    """Process a batch of PDFs and return a list of results."""
    results = []
    for i, path in enumerate(pdf_paths):
        logger.info("Processing PDF %d/%d: %s", i + 1, len(pdf_paths), path)
        result = process_pdf(path, progress_callback=progress_callback)
        result["filename"] = Path(path).name
        results.append(result)
    return results
