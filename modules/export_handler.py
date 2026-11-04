"""
export_handler.py – Export classified transactions to Excel (.xlsx) and CSV (.csv).
"""
import io
import logging
from datetime import datetime
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


def export_to_excel(df: pd.DataFrame, account_info: Dict, reconciliation: Dict) -> bytes:
    """
    Export classified transactions to a professionally formatted Excel workbook.
    Returns bytes that can be downloaded via Streamlit.
    """
    output = io.BytesIO()

    try:
        from openpyxl import Workbook
        from openpyxl.styles import (
            Font, PatternFill, Alignment, Border, Side, numbers
        )
        from openpyxl.utils import get_column_letter
        from openpyxl.worksheet.filters import AutoFilter

        wb = Workbook()

        # ------------------------------------------------------------------ #
        # Sheet 1: Account Summary                                            #
        # ------------------------------------------------------------------ #
        ws_summary = wb.active
        ws_summary.title = "Account Summary"

        TEAL = "3A8D85"
        GOLD = "D9A86C"
        LIGHT_TEAL = "EAF0EC"
        WHITE = "FFFFFF"
        DARK = "172B36"

        def header_style(cell, bg=TEAL, fg=WHITE, bold=True):
            cell.font = Font(name="Calibri", bold=bold, color=fg, size=11)
            cell.fill = PatternFill("solid", fgColor=bg)
            cell.alignment = Alignment(horizontal="left", vertical="center")

        def label_style(cell):
            cell.font = Font(name="Calibri", bold=True, color=DARK, size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")

        def value_style(cell, number_format=None):
            cell.font = Font(name="Calibri", color="24343B", size=10)
            cell.alignment = Alignment(horizontal="left", vertical="center")
            if number_format:
                cell.number_format = number_format

        thin = Side(style="thin", color="CCCCCC")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        # Title
        ws_summary["A1"] = "Bank Statement – Account Summary"
        ws_summary["A1"].font = Font(name="Calibri", bold=True, size=16, color=TEAL)
        ws_summary["A1"].alignment = Alignment(horizontal="left", vertical="center")
        ws_summary.row_dimensions[1].height = 30
        ws_summary.merge_cells("A1:D1")

        ws_summary["A2"] = f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}"
        ws_summary["A2"].font = Font(name="Calibri", italic=True, size=9, color="718096")
        ws_summary.merge_cells("A2:D2")

        # Account info table
        info_rows = [
            ("Account Holder", account_info.get("account_holder", "N/A")),
            ("Account Number", account_info.get("account_number", "N/A")),
            ("Bank Name", account_info.get("bank_name", "N/A")),
            ("IFSC Code", account_info.get("ifsc_code", "N/A")),
            ("Statement Period", account_info.get("statement_period", "N/A")),
            ("Opening Balance (₹)", account_info.get("opening_balance", "N/A")),
            ("Closing Balance (₹)", account_info.get("closing_balance", "N/A")),
        ]

        ws_summary["A4"] = "Account Information"
        header_style(ws_summary["A4"])
        ws_summary.merge_cells("A4:D4")
        ws_summary.row_dimensions[4].height = 22

        for i, (label, value) in enumerate(info_rows, start=5):
            cell_a = ws_summary.cell(row=i, column=1, value=label)
            cell_b = ws_summary.cell(row=i, column=2, value=value)
            label_style(cell_a)
            value_style(cell_b)
            cell_a.border = border
            cell_b.border = border
            if i % 2 == 0:
                cell_a.fill = PatternFill("solid", fgColor=LIGHT_TEAL)
                cell_b.fill = PatternFill("solid", fgColor=LIGHT_TEAL)

        # Reconciliation section
        recon_start = 5 + len(info_rows) + 2
        ws_summary.cell(row=recon_start, column=1, value="Balance Reconciliation").font = Font(
            name="Calibri", bold=True, size=12, color=TEAL
        )
        ws_summary.merge_cells(f"A{recon_start}:D{recon_start}")

        recon_rows = [
            ("Total Debits (₹)", reconciliation.get("total_debits", 0)),
            ("Total Credits (₹)", reconciliation.get("total_credits", 0)),
            ("Calculated Closing Balance (₹)", reconciliation.get("calculated_closing", "N/A")),
            ("Statement Closing Balance (₹)", reconciliation.get("closing_balance", "N/A")),
            ("Difference (₹)", reconciliation.get("difference", "N/A")),
            ("Status", reconciliation.get("status", "unknown").upper()),
        ]

        for j, (label, value) in enumerate(recon_rows, start=recon_start + 1):
            c_a = ws_summary.cell(row=j, column=1, value=label)
            c_b = ws_summary.cell(row=j, column=2, value=value)
            label_style(c_a)
            value_style(c_b, number_format='#,##0.00' if isinstance(value, (int, float)) else None)
            c_a.border = border
            c_b.border = border

        ws_summary.column_dimensions["A"].width = 30
        ws_summary.column_dimensions["B"].width = 25
        ws_summary.column_dimensions["C"].width = 20
        ws_summary.column_dimensions["D"].width = 20

        # ------------------------------------------------------------------ #
        # Sheet 2: Transactions                                               #
        # ------------------------------------------------------------------ #
        ws_txn = wb.create_sheet("Transactions")

        txn_headers = ["Date", "Description", "Debit (₹)", "Credit (₹)", "Balance (₹)",
                       "Category", "Confidence", "Method"]
        for col_idx, header in enumerate(txn_headers, 1):
            cell = ws_txn.cell(row=1, column=col_idx, value=header)
            header_style(cell, bg=DARK)
            ws_txn.row_dimensions[1].height = 20

        display_df = df.copy()
        col_map = {
            "date": "Date", "description": "Description",
            "debit": "Debit (₹)", "credit": "Credit (₹)", "balance": "Balance (₹)",
            "category": "Category", "confidence": "Confidence",
            "classification_method": "Method",
        }

        CORAL = "FFD0C8"
        MINT = "C8EDE8"

        for row_idx, row in display_df.iterrows():
            excel_row = row_idx + 2
            values = {
                "Date": str(row.get("date", "")),
                "Description": str(row.get("description", "")),
                "Debit (₹)": row.get("debit") if pd.notna(row.get("debit")) else "",
                "Credit (₹)": row.get("credit") if pd.notna(row.get("credit")) else "",
                "Balance (₹)": row.get("balance") if pd.notna(row.get("balance")) else "",
                "Category": str(row.get("category", "")),
                "Confidence": row.get("confidence", ""),
                "Method": str(row.get("classification_method", "")),
            }

            for col_idx, header in enumerate(txn_headers, 1):
                val = values.get(header, "")
                cell = ws_txn.cell(row=excel_row, column=col_idx, value=val)
                cell.font = Font(name="Calibri", size=9)
                cell.border = border
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)

                if isinstance(val, (int, float)) and header in ["Debit (₹)", "Credit (₹)", "Balance (₹)"]:
                    cell.number_format = '#,##0.00'
                if header == "Debit (₹)" and val:
                    cell.fill = PatternFill("solid", fgColor=CORAL)
                elif header == "Credit (₹)" and val:
                    cell.fill = PatternFill("solid", fgColor=MINT)
                elif excel_row % 2 == 0:
                    cell.fill = PatternFill("solid", fgColor="F9FAFB")

        # Column widths
        col_widths = [14, 50, 14, 14, 14, 24, 11, 14]
        for i, width in enumerate(col_widths, 1):
            ws_txn.column_dimensions[get_column_letter(i)].width = width

        # Freeze header row
        ws_txn.freeze_panes = "A2"

        # Auto-filter
        ws_txn.auto_filter.ref = f"A1:{get_column_letter(len(txn_headers))}1"

        # ------------------------------------------------------------------ #
        # Sheet 3: Category Summary                                           #
        # ------------------------------------------------------------------ #
        ws_cat = wb.create_sheet("Category Summary")

        cat_headers = ["Category", "Transaction Count", "Total Debit (₹)", "Total Credit (₹)", "% of Total"]
        for col_idx, header in enumerate(cat_headers, 1):
            cell = ws_cat.cell(row=1, column=col_idx, value=header)
            header_style(cell, bg=GOLD, fg=DARK)

        if not df.empty and "category" in df.columns:
            cat_summary = (
                df.groupby("category")
                .agg(
                    count=("description", "count"),
                    total_debit=("debit", "sum"),
                    total_credit=("credit", "sum"),
                )
                .reset_index()
                .sort_values("count", ascending=False)
            )
            total_txns = len(df)
            for row_idx, row in cat_summary.iterrows():
                er = row_idx + 2
                pct = round(row["count"] / total_txns * 100, 1) if total_txns else 0
                vals = [row["category"], int(row["count"]),
                        round(row["total_debit"], 2), round(row["total_credit"], 2), pct]
                for col_idx, val in enumerate(vals, 1):
                    cell = ws_cat.cell(row=er, column=col_idx, value=val)
                    cell.font = Font(name="Calibri", size=10)
                    cell.border = border
                    if isinstance(val, float) and col_idx in [3, 4]:
                        cell.number_format = '#,##0.00'
                    if col_idx == 5:
                        cell.number_format = '0.0"%"'
                    if er % 2 == 0:
                        cell.fill = PatternFill("solid", fgColor=LIGHT_TEAL)

        for col_idx, width in enumerate([28, 20, 18, 18, 14], 1):
            ws_cat.column_dimensions[get_column_letter(col_idx)].width = width
        ws_cat.freeze_panes = "A2"

        wb.save(output)
        output.seek(0)
        return output.getvalue()

    except Exception as exc:
        logger.error("Excel export failed: %s", exc)
        # Return minimal workbook
        wb2 = Workbook() if 'Workbook' in dir() else None
        if wb2 is None:
            return b""
        ws = wb2.active
        ws["A1"] = "Export error – please check logs."
        output2 = io.BytesIO()
        wb2.save(output2)
        return output2.getvalue()


def export_to_csv(df: pd.DataFrame) -> str:
    """Export classified transactions to CSV. Returns CSV string."""
    if df.empty:
        return "date,description,debit,credit,balance,category,confidence,classification_method\n"

    export_cols = ["date", "description", "debit", "credit", "balance",
                   "category", "confidence", "classification_method"]
    available = [c for c in export_cols if c in df.columns]
    return df[available].to_csv(index=False)
