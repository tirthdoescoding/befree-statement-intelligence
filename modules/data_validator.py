"""
data_validator.py – Validate and sanity-check extracted transaction data.
"""
import logging
from typing import Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


def validate_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate transaction DataFrame and return (cleaned_df, warnings).
    """
    warnings = []

    if df.empty:
        return df, ["Transaction table is empty."]

    # Check required columns
    for col in ["date", "description"]:
        if col not in df.columns:
            warnings.append(f"Required column '{col}' is missing from extracted data.")

    # Flag rows with no debit AND no credit
    empty_amount_mask = df["debit"].isna() & df["credit"].isna()
    if empty_amount_mask.any():
        count = empty_amount_mask.sum()
        warnings.append(f"{count} transaction(s) have no debit or credit amount recorded.")

    # Flag duplicate dates with same description (possible parse error)
    if "description" in df.columns:
        dup_mask = df.duplicated(subset=["date", "description"], keep=False)
        if dup_mask.any():
            warnings.append(f"{dup_mask.sum()} potential duplicate transactions detected.")

    # Negative balances (may be valid overdraft but worth flagging)
    if "balance" in df.columns and df["balance"].notna().any():
        neg = (df["balance"] < 0).sum()
        if neg:
            warnings.append(f"{neg} transaction(s) show a negative balance (possible overdraft).")

    return df, warnings


def validate_amounts(df: pd.DataFrame) -> List[str]:
    """Check for unusual amounts."""
    warnings = []
    for col in ["debit", "credit"]:
        if col in df.columns:
            neg = (df[col] < 0).sum() if df[col].notna().any() else 0
            if neg:
                warnings.append(f"{neg} negative value(s) found in '{col}' column — may need manual review.")
    return warnings
