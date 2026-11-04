"""
tests/test_export.py – Tests for Excel and CSV export functionality.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
from modules.export_handler import export_to_excel, export_to_csv


SAMPLE_DF = pd.DataFrame([
    {
        "date": "2024-01-01", "description": "SALARY CREDIT",
        "debit": None, "credit": 75000.0, "balance": 125000.0,
        "category": "Salary", "confidence": 0.95, "classification_method": "rule-based",
    },
    {
        "date": "2024-01-02", "description": "SWIGGY FOOD ORDER",
        "debit": 350.0, "credit": None, "balance": 124650.0,
        "category": "Food & Dining", "confidence": 0.95, "classification_method": "rule-based",
    },
    {
        "date": "2024-01-03", "description": "RANDOM TXN",
        "debit": 1000.0, "credit": None, "balance": 123650.0,
        "category": "Other / Uncategorized", "confidence": 0.0, "classification_method": "fallback",
    },
])

ACCOUNT_INFO = {
    "account_holder": "Test User",
    "account_number": "XXXX1234",
    "bank_name": "Test Bank",
    "ifsc_code": "TEST0001234",
    "statement_period": "01/01/2024 to 31/01/2024",
    "opening_balance": "50000",
    "closing_balance": "123650",
}

RECONCILIATION = {
    "opening_balance": 50000,
    "closing_balance": 123650,
    "total_debits": 1350,
    "total_credits": 75000,
    "calculated_closing": 123650,
    "difference": 0,
    "status": "ok",
    "message": "Balance reconciliation passed.",
}


class TestExcelExport:
    def test_returns_bytes(self):
        result = export_to_excel(SAMPLE_DF, ACCOUNT_INFO, RECONCILIATION)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_valid_xlsx_magic_bytes(self):
        result = export_to_excel(SAMPLE_DF, ACCOUNT_INFO, RECONCILIATION)
        # XLSX files are ZIP archives (start with PK magic bytes)
        assert result[:2] == b"PK"

    def test_empty_dataframe(self):
        result = export_to_excel(pd.DataFrame(), {}, {})
        assert isinstance(result, bytes)

    def test_contains_multiple_sheets(self):
        import zipfile, io
        result = export_to_excel(SAMPLE_DF, ACCOUNT_INFO, RECONCILIATION)
        zf = zipfile.ZipFile(io.BytesIO(result))
        # Check standard XLSX structure
        assert "xl/workbook.xml" in zf.namelist()


class TestCSVExport:
    def test_returns_string(self):
        result = export_to_csv(SAMPLE_DF)
        assert isinstance(result, str)

    def test_has_header(self):
        result = export_to_csv(SAMPLE_DF)
        assert "date" in result.lower()
        assert "description" in result.lower()

    def test_has_correct_row_count(self):
        result = export_to_csv(SAMPLE_DF)
        lines = [l for l in result.strip().splitlines() if l.strip()]
        assert len(lines) == len(SAMPLE_DF) + 1  # +1 for header

    def test_empty_dataframe(self):
        result = export_to_csv(pd.DataFrame())
        assert "date" in result.lower()

    def test_category_in_csv(self):
        result = export_to_csv(SAMPLE_DF)
        assert "Salary" in result
        assert "Food & Dining" in result
