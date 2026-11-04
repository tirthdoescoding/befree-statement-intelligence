"""
generate_sample_pdfs.py – Generate synthetic bank statement PDFs for testing.
Run once to create sample files in data/sample_pdfs/.
"""
import csv
import os
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "data" / "sample_pdfs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


SAMPLE_TRANSACTIONS_SBI = [
    ("01/01/2024", "SALARY CREDIT JAN 2024", "", "75000.00", "125000.00"),
    ("02/01/2024", "UPI/SWIGGY/FOOD ORDER", "450.00", "", "124550.00"),
    ("03/01/2024", "NEFT/RENT PAYMENT/LANDLORD", "15000.00", "", "109550.00"),
    ("04/01/2024", "ATM CASH WITHDRAWAL", "10000.00", "", "99550.00"),
    ("05/01/2024", "AMAZON SHOPPING PURCHASE", "2500.00", "", "97050.00"),
    ("06/01/2024", "AIRTEL BILL PAYMENT", "599.00", "", "96451.00"),
    ("07/01/2024", "HDFC LIFE INSURANCE PREMIUM", "5000.00", "", "91451.00"),
    ("08/01/2024", "SIP HDFC MF JAN 2024", "2000.00", "", "89451.00"),
    ("09/01/2024", "INTEREST CREDIT", "", "250.00", "89701.00"),
    ("10/01/2024", "EMI HOME LOAN PAYMENT", "25000.00", "", "64701.00"),
    ("11/01/2024", "UBER RIDE PAYMENT", "350.00", "", "64351.00"),
    ("12/01/2024", "CONSULTING FEE CREDIT", "", "15000.00", "79351.00"),
    ("13/01/2024", "ELECTRICITY BILL BESCOM", "1200.00", "", "78151.00"),
    ("14/01/2024", "SCHOOL FEE PAYMENT", "8000.00", "", "70151.00"),
    ("15/01/2024", "IRCTC TRAIN TICKET", "1200.00", "", "68951.00"),
]

SAMPLE_TRANSACTIONS_HDFC = [
    ("01/02/2024", "SALARY FEB 2024", "", "80000.00", "80000.00"),
    ("02/02/2024", "ZOMATO FOOD ORDER", "380.00", "", "79620.00"),
    ("03/02/2024", "FLIPKART PURCHASE", "1800.00", "", "77820.00"),
    ("04/02/2024", "JIO RECHARGE", "399.00", "", "77421.00"),
    ("05/02/2024", "APOLLO PHARMACY", "850.00", "", "76571.00"),
    ("06/02/2024", "INDIGO FLIGHT TICKET", "4500.00", "", "72071.00"),
    ("07/02/2024", "ZERODHA STOCK PURCHASE", "5000.00", "", "67071.00"),
    ("08/02/2024", "LIC PREMIUM PAYMENT", "3000.00", "", "64071.00"),
    ("09/02/2024", "FD INTEREST CREDIT", "", "1200.00", "65271.00"),
    ("10/02/2024", "EMI CAR LOAN", "15000.00", "", "50271.00"),
    ("11/02/2024", "PETROL PUMP PAYMENT", "2000.00", "", "48271.00"),
    ("12/02/2024", "HDFC BANK CHARGE", "100.00", "", "48171.00"),
    ("13/02/2024", "COURSERA SUBSCRIPTION", "1500.00", "", "46671.00"),
    ("14/02/2024", "PHONEPE TRANSFER", "5000.00", "", "41671.00"),
    ("15/02/2024", "GST PAYMENT VENDOR", "2500.00", "", "39171.00"),
]


def generate_pdf_reportlab(transactions, bank_name, account_no, holder_name, filename):
    """Generate a text-based PDF bank statement using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(str(OUTPUT_DIR / filename), pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story = []

        # Header
        teal = colors.HexColor("#3A8D85")
        title_style = ParagraphStyle("title", parent=styles["Title"],
                                     fontSize=18, textColor=teal, spaceAfter=6)
        story.append(Paragraph(f"{bank_name} – Account Statement", title_style))
        story.append(Spacer(1, 0.3*cm))

        # Account info
        info_data = [
            ["Account Holder:", holder_name, "Account Number:", account_no],
            ["IFSC Code:", "SBIN0001234", "Statement Period:", "01/01/2024 to 31/01/2024"],
            ["Opening Balance:", "Rs. 50,000.00", "Closing Balance:", f"Rs. {transactions[-1][4]}"],
        ]
        info_table = Table(info_data, colWidths=[4*cm, 5*cm, 4*cm, 5*cm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F7F4")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#3A8D85")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))

        # Transaction table
        txn_header = ["Date", "Description", "Debit (Rs.)", "Credit (Rs.)", "Balance (Rs.)"]
        txn_data = [txn_header] + list(transactions)

        col_widths = [2.5*cm, 8*cm, 3*cm, 3*cm, 3*cm]
        txn_table = Table(txn_data, colWidths=col_widths)
        txn_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172B36")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (1, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EAF0EC")]),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(txn_table)
        story.append(Spacer(1, 0.5*cm))

        footer_style = ParagraphStyle("footer", parent=styles["Normal"],
                                      fontSize=7, textColor=colors.grey)
        story.append(Paragraph(
            "This is a computer-generated statement. No signature required. "
            "For queries contact your branch or customer care.",
            footer_style
        ))

        doc.build(story)
        print(f"  [OK] Generated: {filename}")
        return True
    except ImportError:
        print("  [WARN] ReportLab not available. Generating plain-text PDF fallback.")
        return generate_pdf_plain(transactions, bank_name, account_no, holder_name, filename)
    except Exception as e:
        print(f"  [ERR] Failed to generate {filename}: {e}")
        return False


def generate_pdf_plain(transactions, bank_name, account_no, holder_name, filename):
    """Ultra-simple text PDF fallback using only built-ins."""
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        y = 50
        page.insert_text((40, y), f"{bank_name} – Account Statement", fontsize=16)
        y += 25
        page.insert_text((40, y), f"Account Holder: {holder_name}  |  Account: {account_no}", fontsize=10)
        y += 15
        page.insert_text((40, y), "IFSC: SBIN0001234  |  Statement Period: 01/01/2024 to 31/01/2024", fontsize=10)
        y += 15
        page.insert_text((40, y), "Opening Balance: Rs. 50,000.00", fontsize=10)
        y += 25
        # Header
        page.insert_text((40, y), "Date        Description                                   Debit      Credit     Balance", fontsize=8)
        y += 15
        for txn in transactions:
            line = f"{txn[0]:<12}{txn[1][:40]:<42}{txn[2]:>10} {txn[3]:>10} {txn[4]:>12}"
            page.insert_text((40, y), line, fontsize=8)
            y += 13
            if y > 800:
                page = doc.new_page(width=595, height=842)
                y = 50
        doc.save(str(OUTPUT_DIR / filename))
        doc.close()
        print(f"  [OK] Generated (plain): {filename}")
        return True
    except Exception as e:
        print(f"  [ERR] Plain PDF also failed: {e}")
        return False


if __name__ == "__main__":
    print("Generating sample bank statement PDFs...")
    generate_pdf_reportlab(
        SAMPLE_TRANSACTIONS_SBI,
        "State Bank of India",
        "XXXX1234",
        "Rajesh Kumar Sharma",
        "sbi_statement_jan2024.pdf",
    )
    generate_pdf_reportlab(
        SAMPLE_TRANSACTIONS_HDFC,
        "HDFC Bank",
        "XXXX5678",
        "Priya Mehta",
        "hdfc_statement_feb2024.pdf",
    )
    print(f"\nSample PDFs saved to: {OUTPUT_DIR}")
