"""
tests/test_validation.py – Tests for data validation and reconciliation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
from modules.data_validator import validate_transactions, validate_amounts
from modules.reconciliation import reconcile


class TestDataValidator:
    def test_empty_df(self):
        df = pd.DataFrame()
        _, warnings = validate_transactions(df)
        assert len(warnings) > 0

    def test_valid_df(self):
        df = pd.DataFrame([
            {"date": "2024-01-01", "description": "SALARY", "debit": None, "credit": 75000, "balance": 125000},
            {"date": "2024-01-02", "description": "ATM", "debit": 5000, "credit": None, "balance": 120000},
        ])
        df, warnings = validate_transactions(df)
        assert isinstance(df, pd.DataFrame)

    def test_flags_no_amount(self):
        df = pd.DataFrame([
            {"date": "2024-01-01", "description": "SALARY", "debit": None, "credit": None, "balance": 125000},
        ])
        _, warnings = validate_transactions(df)
        assert any("no debit or credit" in w.lower() for w in warnings)


class TestReconciliation:
    def test_balanced(self):
        df = pd.DataFrame([
            {"debit": None, "credit": 75000},
            {"debit": 5000, "credit": None},
        ])
        account = {"opening_balance": "50000", "closing_balance": "120000"}
        result = reconcile(df, account)
        assert result["status"] == "ok"
        assert result["total_credits"] == 75000
        assert result["total_debits"] == 5000

    def test_unbalanced(self):
        df = pd.DataFrame([
            {"debit": None, "credit": 75000},
            {"debit": 5000, "credit": None},
        ])
        account = {"opening_balance": "50000", "closing_balance": "999999"}
        result = reconcile(df, account)
        assert result["status"] == "warning"
        assert result["difference"] is not None and result["difference"] > 1

    def test_no_opening_balance(self):
        df = pd.DataFrame([{"debit": 100, "credit": None}])
        result = reconcile(df, {})
        assert result["status"] == "unknown"

    def test_calculated_closing(self):
        df = pd.DataFrame([
            {"debit": None, "credit": 1000},
            {"debit": 300, "credit": None},
        ])
        account = {"opening_balance": "5000"}
        result = reconcile(df, account)
        assert result["calculated_closing"] == 5700.0
