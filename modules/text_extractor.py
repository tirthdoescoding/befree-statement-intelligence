"""
text_extractor.py – Extract text and transaction data from text-based PDFs using pdfplumber.
"""
import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """Extract raw text from each page of a text-based PDF."""
    pages_text = []
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
    except Exception as exc:
        logger.error("Text extraction failed: %s", exc)
    return pages_text


def extract_tables_from_pdf(pdf_path: str) -> List[List[List]]:
    """Extract tables from each page using pdfplumber's table detection."""
    all_tables = []
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables() or []
                all_tables.extend(tables)
    except Exception as exc:
        logger.error("Table extraction failed: %s", exc)
    return all_tables


def extract_account_info(text: str) -> Dict[str, str]:
    """
    Extract account holder information from raw text.
    Handles various Indian bank statement formats.
    """
    info = {
        "account_holder": "",
        "account_number": "",
        "ifsc_code": "",
        "bank_name": "",
        "statement_period": "",
        "opening_balance": "",
        "closing_balance": "",
    }

    # Account Holder Name
    for pattern in [
        r"(?:Account\s*Holder|Customer\s*Name|Name)\s*[:\-]?\s*([A-Z][A-Za-z\s\.]+)",
        r"(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][A-Za-z\s\.]+)",
        r"Statement\s+of\s+(?:Account\s+of\s+)?([A-Z][A-Za-z\s\.]+)",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            info["account_holder"] = m.group(1).strip()[:60]
            break

    # Account Number
    for pattern in [
        r"Account\s*(?:Number|No\.?|#)\s*[:\-]?\s*([X\d]{4,20})",
        r"A/c\s*(?:No\.?|Number)?\s*[:\-]?\s*([X\d]{4,20})",
        r"Acc(?:ount)?\s*No\.\s*[:\-]?\s*([X\d]{4,20})",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            info["account_number"] = m.group(1).strip()
            break

    # IFSC Code
    m = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", text)
    if m:
        info["ifsc_code"] = m.group(1)

    # Bank Name
    bank_patterns = [
        r"(State Bank of India|SBI)",
        r"(HDFC Bank)",
        r"(ICICI Bank)",
        r"(Axis Bank)",
        r"(Kotak Mahindra Bank|Kotak Bank)",
        r"(Punjab National Bank|PNB)",
        r"(Bank of Baroda|BOB)",
        r"(Canara Bank)",
        r"(Union Bank of India|Union Bank)",
        r"(IndusInd Bank)",
        r"(Yes Bank)",
        r"(IDFC First Bank|IDFC Bank)",
        r"(Federal Bank)",
        r"(Bank of India|BOI)",
        r"(Central Bank of India)",
        r"(Indian Bank)",
    ]
    for pattern in bank_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            info["bank_name"] = m.group(1)
            break

    # Statement Period
    for pattern in [
        r"(?:Statement\s+Period|Period|From)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s*(?:to|–|-)\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",
        r"(\d{1,2}\s+\w+\s+\d{4})\s*(?:to|–|-)\s*(\d{1,2}\s+\w+\s+\d{4})",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            info["statement_period"] = f"{m.group(1)} to {m.group(2)}"
            break

    # Opening Balance
    for pattern in [
        r"(?:Opening|Open\.?)\s*(?:Balance|Bal\.?)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
        r"(?:Balance\s+B/F|Bal\.\s*B/F)\s*[:\-]?\s*([\d,]+\.?\d*)",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            info["opening_balance"] = m.group(1).replace(",", "")
            break

    # Closing Balance
    for pattern in [
        r"(?:Closing|Close\.?)\s*(?:Balance|Bal\.?)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+\.?\d*)",
        r"(?:Balance\s+C/F|Bal\.\s*C/F)\s*[:\-]?\s*([\d,]+\.?\d*)",
    ]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            info["closing_balance"] = m.group(1).replace(",", "")
            break

    return info
