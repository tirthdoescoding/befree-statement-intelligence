"""
database.py – SQLite-based processing history storage.
"""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "history.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite history database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS processing_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            processed_at TEXT NOT NULL,
            pdf_type TEXT,
            pages INTEGER,
            transaction_count INTEGER,
            account_holder TEXT,
            account_number TEXT,
            bank_name TEXT,
            opening_balance REAL,
            closing_balance REAL,
            total_debits REAL,
            total_credits REAL,
            reconciliation_status TEXT,
            warnings TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            txn_date TEXT,
            description TEXT,
            debit REAL,
            credit REAL,
            balance REAL,
            category TEXT,
            confidence REAL,
            classification_method TEXT,
            FOREIGN KEY (session_id) REFERENCES processing_sessions(id)
        )
    """)
    conn.commit()
    conn.close()


def save_session(
    filename: str,
    pdf_type: str,
    pages: int,
    df: pd.DataFrame,
    account_info: Dict,
    reconciliation: Dict,
    warnings: List[str],
) -> int:
    """Save a processing session to the database. Returns the session ID."""
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO processing_sessions
        (filename, processed_at, pdf_type, pages, transaction_count,
         account_holder, account_number, bank_name, opening_balance, closing_balance,
         total_debits, total_credits, reconciliation_status, warnings)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        filename,
        datetime.now().isoformat(),
        pdf_type,
        pages,
        len(df),
        account_info.get("account_holder", ""),
        account_info.get("account_number", ""),
        account_info.get("bank_name", ""),
        _safe_float(account_info.get("opening_balance")),
        _safe_float(account_info.get("closing_balance")),
        reconciliation.get("total_debits", 0),
        reconciliation.get("total_credits", 0),
        reconciliation.get("status", "unknown"),
        json.dumps(warnings),
    ))
    session_id = cur.lastrowid

    if not df.empty:
        rows = []
        for _, row in df.iterrows():
            rows.append((
                session_id,
                str(row.get("date", "")),
                str(row.get("description", "")),
                _safe_float(row.get("debit")),
                _safe_float(row.get("credit")),
                _safe_float(row.get("balance")),
                str(row.get("category", "")),
                _safe_float(row.get("confidence")),
                str(row.get("classification_method", "")),
            ))
        cur.executemany("""
            INSERT INTO transactions
            (session_id, txn_date, description, debit, credit, balance, category, confidence, classification_method)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, rows)

    conn.commit()
    conn.close()
    return session_id


def get_sessions() -> List[Dict]:
    """Return all processing sessions (most recent first)."""
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM processing_sessions ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_session_transactions(session_id: int) -> pd.DataFrame:
    """Return transactions for a given session as a DataFrame."""
    init_db()
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE session_id = ?",
        conn, params=(session_id,)
    )
    conn.close()
    return df


def _safe_float(val) -> Optional[float]:
    try:
        return float(str(val).replace(",", "")) if val is not None else None
    except (ValueError, TypeError):
        return None
