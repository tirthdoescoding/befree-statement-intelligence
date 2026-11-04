"""
reconciliation.py – Balance reconciliation: verify that
Opening Balance + Credits - Debits ≈ Closing Balance.
"""
import logging
from typing import Dict, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

TOLERANCE = 1.0  # Allow ₹1 rounding difference


def reconcile(
    df: pd.DataFrame,
    account_info: Dict,
) -> Dict:
    """
    Perform balance reconciliation.

    Returns a dict:
        {
            "opening_balance": float | None,
            "closing_balance": float | None,
            "total_debits": float,
            "total_credits": float,
            "calculated_closing": float | None,
            "difference": float | None,
            "status": "ok" | "warning" | "unknown",
            "message": str,
        }
    """
    total_debits = df["debit"].fillna(0).sum()
    total_credits = df["credit"].fillna(0).sum()

    opening = _parse_balance(account_info.get("opening_balance"))
    closing = _parse_balance(account_info.get("closing_balance"))

    result = {
        "total_debits": round(total_debits, 2),
        "total_credits": round(total_credits, 2),
        "opening_balance": opening,
        "closing_balance": closing,
        "calculated_closing": None,
        "difference": None,
        "status": "unknown",
        "message": "Opening/closing balance not found in statement.",
    }

    if opening is not None:
        calculated = round(opening + total_credits - total_debits, 2)
        result["calculated_closing"] = calculated

        if closing is not None:
            diff = abs(closing - calculated)
            result["difference"] = round(diff, 2)
            if diff <= TOLERANCE:
                result["status"] = "ok"
                result["message"] = f"✅ Balance reconciliation passed. Difference: ₹{diff:.2f}"
            else:
                result["status"] = "warning"
                result["message"] = (
                    f"⚠️ Balance mismatch detected. Expected closing balance: ₹{calculated:,.2f}, "
                    f"Statement closing balance: ₹{closing:,.2f}, Difference: ₹{diff:,.2f}. "
                    "This may be due to unrecorded transactions, fees, or multi-statement extraction."
                )
        else:
            result["status"] = "unknown"
            result["message"] = f"Closing balance not found. Calculated closing balance: ₹{calculated:,.2f}"

    return result


def _parse_balance(val) -> Optional[float]:
    """Parse a balance value from account_info (string or None)."""
    if val is None:
        return None
    try:
        cleaned = str(val).replace(",", "").replace("₹", "").replace("Rs.", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None
