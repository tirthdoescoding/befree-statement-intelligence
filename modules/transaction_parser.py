"""
transaction_parser.py – Parse transaction rows from raw extracted text.
Handles multi-page, wrapped descriptions, various date formats, and
debit/credit/balance amount normalisation.
"""
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Date patterns (ordered most→least specific)
# ---------------------------------------------------------------------------
DATE_PATTERNS = [
    r"\d{2}/\d{2}/\d{4}",   # DD/MM/YYYY
    r"\d{2}-\d{2}-\d{4}",   # DD-MM-YYYY
    r"\d{2}\.\d{2}\.\d{4}", # DD.MM.YYYY
    r"\d{4}/\d{2}/\d{2}",   # YYYY/MM/DD
    r"\d{4}-\d{2}-\d{2}",   # YYYY-MM-DD
    r"\d{2}/\d{2}/\d{2}",   # DD/MM/YY
    r"\d{2}-\d{2}-\d{2}",   # DD-MM-YY
    r"\d{1,2}\s+\w{3}\s+\d{4}",  # D MMM YYYY
    r"\d{1,2}\s+\w+\s+\d{4}",    # D Month YYYY
]

DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
    "%Y/%m/%d", "%Y-%m-%d",
    "%d/%m/%y", "%d-%m-%y",
    "%d %b %Y", "%d %B %Y",
]


def parse_date(date_str: str) -> Optional[datetime]:
    """Try to parse a date string into a datetime object."""
    if not date_str:
        return None
    cleaned = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def parse_amount(amount_str: str) -> Optional[float]:
    """
    Parse a currency amount string to a float.
    Handles: commas, CR/DR suffixes, negative signs, empty strings.
    """
    if not amount_str or str(amount_str).strip() in ("", "-", "–", "N/A", "nil", "Nil"):
        return None
    s = str(amount_str).strip()
    negative = False
    if s.upper().endswith("DR") or s.startswith("-"):
        negative = True
    s = re.sub(r"[^\d.]", "", s)
    if not s:
        return None
    try:
        value = float(s)
        return -value if negative else value
    except ValueError:
        return None


def _has_date(line: str) -> bool:
    """Return True if the line starts with something that looks like a date."""
    for pat in DATE_PATTERNS:
        if re.match(r"^\s*" + pat, line):
            return True
    return False


def parse_transactions_from_text(pages_text: List[str]) -> List[Dict]:
    """
    Parse transaction rows from raw extracted text using heuristics.
    Works across multiple pages, handles wrapped descriptions.
    """
    full_text = "\n".join(pages_text)
    lines = full_text.splitlines()

    transactions = []
    pending: Optional[Dict] = None

    # Regex to capture a transaction line:
    # DATE  DESCRIPTION  [DEBIT]  [CREDIT]  BALANCE
    TXN_RE = re.compile(
        r"^(?P<date>\d{1,2}[\-/\.]\d{1,2}[\-/\.]\d{2,4}|\d{4}[\-/]\d{2}[\-/]\d{2}|\d{1,2}\s+\w{3}\s+\d{4})"
        r"\s+"
        r"(?P<desc>.+?)\s+"
        r"(?P<amt1>[\d,]+\.\d{2}(?:\s*(?:CR|DR))?|-)\s+"
        r"(?P<amt2>[\d,]+\.\d{2}(?:\s*(?:CR|DR))?|-)?\s*"
        r"(?P<bal>[\d,]+\.\d{2}(?:\s*(?:CR|DR))?)?\s*$",
        re.IGNORECASE,
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue

        m = TXN_RE.match(line)
        if m:
            if pending:
                transactions.append(pending)

            date_obj = parse_date(m.group("date"))
            amt1 = parse_amount(m.group("amt1"))
            amt2 = parse_amount(m.group("amt2"))
            bal = parse_amount(m.group("bal"))

            # Determine debit/credit from values
            debit, credit = None, None
            raw1 = (m.group("amt1") or "").upper()
            raw2 = (m.group("amt2") or "").upper()

            if "CR" in raw1:
                credit = abs(amt1) if amt1 is not None else None
            elif amt1 is not None and amt1 != 0:
                debit = abs(amt1)

            if "CR" in raw2:
                credit = abs(amt2) if amt2 is not None else None
            elif amt2 is not None and amt2 != 0:
                credit = abs(amt2)

            pending = {
                "date": date_obj.strftime("%Y-%m-%d") if date_obj else m.group("date"),
                "description": m.group("desc").strip(),
                "debit": debit,
                "credit": credit,
                "balance": bal,
            }
        elif pending and not _has_date(line):
            # Likely a continuation of the previous description
            if len(line) < 100:
                pending["description"] += " " + line

    if pending:
        transactions.append(pending)

    return transactions


def parse_transactions_from_table(tables: List[List[List]]) -> List[Dict]:
    """
    Parse transactions from pdfplumber-extracted table data.
    Attempts to auto-detect column positions.
    """
    transactions = []

    for table in tables:
        if not table or len(table) < 2:
            continue

        header = [str(c).lower().strip() if c else "" for c in table[0]]

        # Identify column indices
        date_col = _find_col(header, ["date", "txn date", "value date", "posting date"])
        desc_col = _find_col(header, ["description", "particulars", "narration", "details", "remarks"])
        debit_col = _find_col(header, ["debit", "dr", "withdrawal", "withdrawals", "dr amount"])
        credit_col = _find_col(header, ["credit", "cr", "deposit", "deposits", "cr amount"])
        bal_col = _find_col(header, ["balance", "bal", "running balance"])

        if date_col is None:
            continue  # Can't use this table without a date column

        for row in table[1:]:
            if not row or all(c is None or str(c).strip() == "" for c in row):
                continue

            def safe_get(idx):
                if idx is None or idx >= len(row):
                    return None
                v = row[idx]
                return str(v).strip() if v is not None else None

            date_str = safe_get(date_col)
            if not date_str:
                continue

            date_obj = parse_date(date_str)
            if not date_obj:
                continue

            desc = safe_get(desc_col) or ""
            debit = parse_amount(safe_get(debit_col))
            credit = parse_amount(safe_get(credit_col))
            balance = parse_amount(safe_get(bal_col))

            if not desc and debit is None and credit is None:
                continue

            transactions.append({
                "date": date_obj.strftime("%Y-%m-%d"),
                "description": desc,
                "debit": debit,
                "credit": credit,
                "balance": balance,
            })

    return transactions


def _find_col(headers: List[str], candidates: List[str]) -> Optional[int]:
    """Find the index of the best matching column header."""
    for candidate in candidates:
        for i, h in enumerate(headers):
            if candidate in h:
                return i
    return None


def deduplicate_transactions(transactions: List[Dict]) -> List[Dict]:
    """Remove duplicate transactions based on date + description + amounts."""
    seen = set()
    unique = []
    for txn in transactions:
        key = (txn.get("date"), txn.get("description", "")[:40], txn.get("debit"), txn.get("credit"))
        if key not in seen:
            seen.add(key)
            unique.append(txn)
    return unique


def normalize_transactions(transactions: List[Dict]) -> pd.DataFrame:
    """
    Convert list of transaction dicts to a clean pandas DataFrame.
    Normalises types and handles missing values.
    """
    if not transactions:
        return pd.DataFrame(columns=["date", "description", "debit", "credit", "balance"])

    df = pd.DataFrame(transactions)

    # Ensure required columns
    for col in ["date", "description", "debit", "credit", "balance"]:
        if col not in df.columns:
            df[col] = None

    df["debit"] = pd.to_numeric(df["debit"], errors="coerce")
    df["credit"] = pd.to_numeric(df["credit"], errors="coerce")
    df["balance"] = pd.to_numeric(df["balance"], errors="coerce")
    df["description"] = df["description"].fillna("").str.strip()

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    return df
