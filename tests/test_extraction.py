"""
tests/test_extraction.py – Tests for PDF extraction and transaction parsing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
from modules.transaction_parser import (
    parse_date, parse_amount, deduplicate_transactions,
    normalize_transactions, parse_transactions_from_table,
)
from modules.text_extractor import extract_account_info


class TestDateParsing:
    def test_dd_mm_yyyy_slash(self):
        d = parse_date("01/01/2024")
        assert d is not None
        assert d.year == 2024 and d.month == 1 and d.day == 1

    def test_dd_mm_yyyy_dash(self):
        d = parse_date("15-03-2024")
        assert d is not None
        assert d.day == 15 and d.month == 3

    def test_yyyy_mm_dd(self):
        d = parse_date("2024-06-20")
        assert d is not None
        assert d.year == 2024

    def test_dd_mon_yyyy(self):
        d = parse_date("05 Jan 2024")
        assert d is not None
        assert d.month == 1

    def test_invalid_date(self):
        d = parse_date("not-a-date")
        assert d is None

    def test_empty_date(self):
        d = parse_date("")
        assert d is None


class TestAmountParsing:
    def test_simple_amount(self):
        assert parse_amount("1500.00") == 1500.0

    def test_amount_with_comma(self):
        assert parse_amount("1,50,000.00") == 150000.0

    def test_dr_suffix(self):
        val = parse_amount("5000.00DR")
        assert val == -5000.0

    def test_cr_suffix(self):
        val = parse_amount("5000.00CR")
        assert val == 5000.0

    def test_negative_amount(self):
        val = parse_amount("-250.00")
        assert val == -250.0

    def test_empty_amount(self):
        assert parse_amount("") is None
        assert parse_amount("-") is None
        assert parse_amount("N/A") is None

    def test_nil(self):
        assert parse_amount("nil") is None


class TestDeduplication:
    def test_removes_exact_duplicates(self):
        txns = [
            {"date": "2024-01-01", "description": "SALARY", "debit": None, "credit": 75000},
            {"date": "2024-01-01", "description": "SALARY", "debit": None, "credit": 75000},
            {"date": "2024-01-02", "description": "ATM", "debit": 5000, "credit": None},
        ]
        unique = deduplicate_transactions(txns)
        assert len(unique) == 2

    def test_keeps_different_transactions(self):
        txns = [
            {"date": "2024-01-01", "description": "SALARY", "debit": None, "credit": 75000},
            {"date": "2024-01-02", "description": "ATM", "debit": 5000, "credit": None},
        ]
        unique = deduplicate_transactions(txns)
        assert len(unique) == 2


class TestNormalization:
    def test_empty_list(self):
        df = normalize_transactions([])
        assert df.empty

    def test_basic_normalization(self):
        txns = [
            {"date": "01/01/2024", "description": "SALARY", "debit": None, "credit": 75000, "balance": 125000},
            {"date": "02/01/2024", "description": "ATM", "debit": 5000, "credit": None, "balance": 120000},
        ]
        df = normalize_transactions(txns)
        assert len(df) == 2
        assert "date" in df.columns
        assert "debit" in df.columns
        assert "credit" in df.columns

    def test_sorts_by_date(self):
        txns = [
            {"date": "15/01/2024", "description": "B", "debit": 100, "credit": None, "balance": 900},
            {"date": "01/01/2024", "description": "A", "debit": 200, "credit": None, "balance": 800},
        ]
        df = normalize_transactions(txns)
        assert df.iloc[0]["description"] == "A"


class TestTableParsing:
    def test_parse_standard_table(self):
        tables = [[
            ["Date", "Description", "Debit", "Credit", "Balance"],
            ["01/01/2024", "SALARY CREDIT", "", "75000.00", "125000.00"],
            ["02/01/2024", "SWIGGY FOOD", "350.00", "", "124650.00"],
        ]]
        txns = parse_transactions_from_table(tables)
        assert len(txns) >= 1

    def test_empty_table(self):
        txns = parse_transactions_from_table([])
        assert txns == []

    def test_table_missing_date_col(self):
        tables = [[["Description", "Amount"], ["SALARY", "75000"]]]
        txns = parse_transactions_from_table(tables)
        assert txns == []


class TestAccountInfoExtraction:
    SAMPLE_TEXT = """
    State Bank of India
    Account Statement
    Account Holder: Rajesh Kumar Sharma
    Account Number: XXXX1234
    IFSC Code: SBIN0001234
    Statement Period: 01/01/2024 to 31/01/2024
    Opening Balance: Rs. 50,000.00
    Closing Balance: Rs. 68,951.00
    """

    def test_extracts_bank_name(self):
        info = extract_account_info(self.SAMPLE_TEXT)
        assert "State Bank of India" in info.get("bank_name", "")

    def test_extracts_account_holder(self):
        info = extract_account_info(self.SAMPLE_TEXT)
        assert "Rajesh" in info.get("account_holder", "")

    def test_extracts_ifsc(self):
        info = extract_account_info(self.SAMPLE_TEXT)
        assert info.get("ifsc_code") == "SBIN0001234"

    def test_extracts_period(self):
        info = extract_account_info(self.SAMPLE_TEXT)
        assert info.get("statement_period") != ""

    def test_extracts_opening_balance(self):
        info = extract_account_info(self.SAMPLE_TEXT)
        assert info.get("opening_balance") == "50000.00"
