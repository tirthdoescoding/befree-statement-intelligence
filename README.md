# 🏦 BankSight – Bank Statement Processing & Classification System

> **Befree Automation Internship | Technical Assessment Round 2**

A production-quality, end-to-end bank statement processing system that extracts, classifies, and exports financial transaction data from PDF bank statements — without using any LLM or generative AI.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Features](#features)
5. [Technology Stack](#technology-stack)
6. [System Architecture](#system-architecture)
7. [Data Processing Workflow](#data-processing-workflow)
8. [PDF Extraction Methodology](#pdf-extraction-methodology)
9. [OCR Methodology](#ocr-methodology)
10. [Classification Methodology](#classification-methodology)
11. [Why No LLM](#why-no-llm)
12. [Installation](#installation)
13. [Running the Application](#running-the-application)
14. [Usage Guide](#usage-guide)
15. [Sample Input & Output](#sample-input--output)
16. [Export Instructions](#export-instructions)
17. [Testing](#testing)
18. [Project Structure](#project-structure)
19. [Limitations](#limitations)
20. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

**BankSight** is a fully functional bank statement processing and classification system built with Python. It accepts PDF bank statements from Indian banks (SBI, HDFC, ICICI, Axis, etc.), automatically extracts account information and transaction data, classifies each transaction into meaningful financial categories using a hybrid rule-based + ML engine, and exports the results to Excel or CSV.

The system handles both **text-based PDFs** (digital/e-statements) and **image-based PDFs** (scanned physical statements) through an intelligent detection and fallback pipeline.

---

## 📌 Problem Statement

Indian bank statements come in dozens of formats — different banks, different layouts, different column orders, different date formats, and varying text quality (especially scanned PDFs). Manual processing of these statements is time-consuming and error-prone.

This system solves:
- Automated extraction of structured transaction data from unstructured PDF statements
- Intelligent classification of transactions by type (Salary, Rent, Food, etc.)
- Financial reconciliation validation
- Professional export to Excel/CSV for further analysis

---

## 🎯 Objectives

- Accept and process PDF bank statements from multiple banks
- Detect whether a PDF is text-based or image-based (scanned)
- Extract account holder details and full transaction history
- Classify transactions using non-LLM approaches (rule-based + ML)
- Validate extracted data with balance reconciliation
- Export processed data to professionally formatted Excel and CSV
- Provide an interactive, modern web UI for all operations

---

## ✨ Features

### Core Features
- ✅ **Multi-PDF Upload** — Process one or more statements in a batch
- ✅ **Auto PDF Type Detection** — Text vs. scanned detection per page
- ✅ **Text Extraction** — pdfplumber for structured text and table extraction
- ✅ **OCR Fallback** — Tesseract + OpenCV for scanned PDFs
- ✅ **Account Info Extraction** — Name, Account No., IFSC, Bank, Period, Balances
- ✅ **Transaction Parsing** — Multi-page, wrapped descriptions, date/amount normalisation
- ✅ **Duplicate Detection** — Removes repeated transactions
- ✅ **Hybrid Classification** — Rule-based + TF-IDF/LinearSVC ML
- ✅ **17 Transaction Categories** — Salary, Food, Shopping, Rent, Utilities, etc.
- ✅ **Confidence Scoring** — Each classification has a confidence score (0–1)
- ✅ **Manual Override** — Users can correct any category
- ✅ **Balance Reconciliation** — Validates Opening + Credits − Debits ≈ Closing
- ✅ **Excel Export** — 3-sheet workbook (Account Summary, Transactions, Category Summary)
- ✅ **CSV Export** — Clean flat-file export
- ✅ **Processing History** — SQLite-backed session history
- ✅ **Custom Rules** — Add your own keyword classification rules at runtime
- ✅ **62 Automated Tests** — pytest coverage across all modules

### UI Features
- 🎨 Premium FinTech SaaS design (Deep Navy + Muted Teal + Champagne Gold)
- 📊 Interactive Plotly charts (donut, bar, horizontal bar)
- 🃏 KPI cards with key financial metrics
- 🔎 Filter by category, date range, debit/credit, search
- ⚡ Animated processing steps with progress bar
- 📱 Responsive layout

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| UI Framework | Streamlit |
| Text PDF Extraction | pdfplumber |
| PDF Processing | PyMuPDF (fitz) |
| OCR Engine | Tesseract + pytesseract |
| Image Preprocessing | OpenCV |
| Data Processing | Pandas |
| ML Classification | scikit-learn (TF-IDF + LinearSVC) |
| Excel Export | openpyxl |
| PDF Generation (samples) | ReportLab |
| Charts | Plotly |
| Local Storage | SQLite3 |
| Testing | pytest |

---

## 🏗️ System Architecture

```
bank_statement_processor/
│
├── app.py                      ← Streamlit UI (all pages + routing)
├── generate_sample_pdfs.py     ← Sample PDF generator
├── requirements.txt
├── README.md
├── .gitignore
│
├── modules/                    ← Core processing modules
│   ├── pdf_detector.py         ← Text vs. image PDF detection
│   ├── pdf_handler.py          ← Validation, encryption check
│   ├── text_extractor.py       ← pdfplumber text + table extraction
│   ├── ocr_engine.py           ← Tesseract OCR pipeline
│   ├── transaction_parser.py   ← Transaction row parsing & normalisation
│   ├── bank_parser.py          ← Orchestration: detect → extract → parse
│   ├── rule_engine.py          ← Keyword/pattern rule-based classifier
│   ├── ml_classifier.py        ← TF-IDF + LinearSVC ML classifier
│   ├── classification_engine.py← Hybrid 3-layer classification
│   ├── data_validator.py       ← Transaction validation
│   ├── reconciliation.py       ← Balance reconciliation
│   ├── export_handler.py       ← Excel + CSV export
│   └── database.py             ← SQLite history storage
│
├── config/
│   ├── categories.json          ← 17 categories with colours
│   └── classification_rules.json← Configurable keyword rules
│
├── data/
│   ├── sample_transactions.csv  ← Training data for ML model
│   ├── history.db               ← SQLite history (auto-created)
│   └── sample_pdfs/             ← Generated test PDFs
│
├── models/
│   ├── tfidf_vectorizer.pkl     ← Saved TF-IDF model (auto-generated)
│   └── svc_classifier.pkl       ← Saved LinearSVC model (auto-generated)
│
└── tests/
    ├── test_classification.py
    ├── test_extraction.py
    ├── test_validation.py
    └── test_export.py
```

---

## 🔄 Data Processing Workflow

```
PDF Upload
    ↓
File Validation (size, type, corruption, password)
    ↓
PDF Type Detection (text ratio per page via PyMuPDF)
    ↓
Text Extraction (pdfplumber) ──OR── OCR (Tesseract + OpenCV)
    ↓
Account Information Extraction (regex patterns)
    ↓
Transaction Table Parsing (table-aware + text heuristics)
    ↓
Data Cleaning & Normalisation (dates, amounts, descriptions)
    ↓
Duplicate Detection
    ↓
Transaction Validation
    ↓
Hybrid Classification Engine:
    Layer 1: Rule-based Heuristics (keyword/pattern matching)
    Layer 2: TF-IDF + LinearSVC ML
    Layer 3: Fallback → Other / Uncategorized
    ↓
Confidence Scoring
    ↓
Balance Reconciliation (Opening + Credits − Debits ≈ Closing)
    ↓
Dashboard Visualisation + Manual Correction
    ↓
SQLite History Storage
    ↓
Excel / CSV Export
```

---

## 📄 PDF Extraction Methodology

### Text-Based PDFs
1. **Detection** — PyMuPDF scans each page; if >50 chars of extractable text exist, it's classified as text-based.
2. **Table Extraction** — `pdfplumber.extract_tables()` locates tabular data with column detection.
3. **Text Parsing** — Full page text is searched with regex patterns for account info and transaction rows.
4. **Column Mapping** — Column headers are matched against known names (Date, Description, Debit, Credit, Balance) using fuzzy substring matching.

### Account Information Extraction
Regex patterns extract:
- Account holder name (matches `Account Holder: NAME` patterns)
- Account number (matches `Acc No: XXXX1234` patterns)
- IFSC code (matches IFSC format `ABCD0123456`)
- Bank name (matched against 15 major Indian bank patterns)
- Statement period (matched as date range)
- Opening/closing balance (matched with Rs./₹ prefixes)

---

## 🖼️ OCR Methodology

For scanned/image PDFs:

1. **Page to Image** — PyMuPDF renders each page at 300 DPI to a numpy array.
2. **Preprocessing (OpenCV)**:
   - Grayscale conversion
   - Noise reduction (`fastNlMeansDenoising`)
   - Otsu's binarisation threshold
   - Deskew correction (rotation angle detection via `minAreaRect`)
3. **Tesseract OCR** — `--oem 3 --psm 6` configuration, optimised for structured table data.
4. **Text Pipeline** — OCR text is then processed through the same text parsing pipeline.

**Fallback:** If Tesseract is not installed, the system falls back to pdfplumber text extraction with a warning.

---

## 🏷️ Classification Methodology

### Why No LLM?
LLMs are **not used** because:
- They require expensive API calls or large GPU hardware
- They introduce non-determinism (same input → different outputs)
- They have privacy concerns (sending financial data to external servers)
- They are slow for batch processing
- Traditional rule-based + ML approaches achieve >95% accuracy for this structured classification task
- The classification vocabulary is well-defined and finite

### Layer 1: Rule-Based Heuristic Engine
- **Source:** `config/classification_rules.json` (fully configurable without code changes)
- **Method:** Keyword dictionary + regex pattern matching against transaction descriptions
- **Features:** Priority ordering, direction filter (debit/credit only rules), word-boundary matching for short keywords
- **Confidence:** 0.95 when a rule matches
- **Coverage:** 16 category-specific rule sets with 150+ keywords

### Layer 2: Traditional ML (TF-IDF + LinearSVC)
- **Vectorizer:** Character n-gram TF-IDF (n=2–4, 5000 features, sublinear TF)
- **Classifier:** Linear Support Vector Classifier (C=1.0, balanced class weights)
- **Training Data:** `data/sample_transactions.csv` (58 labelled samples across 16 categories)
- **Model Persistence:** Saved to `models/` as pickle files, auto-reloads on startup
- **Confidence:** Derived from SVM decision function margin, normalised via sigmoid

### Layer 3: Fallback
- Assigns "Other / Uncategorized" with confidence 0.0 when neither layer produces a confident classification

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/bank_statement_processor.git
cd bank_statement_processor
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR (for Scanned PDFs)

> Tesseract is **optional** — only required for scanned/image-based PDFs.
> Text-based PDFs work without Tesseract.

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default path: `C:\Program Files\Tesseract-OCR\`)
3. Add Tesseract to PATH or the application will auto-detect it

**Verify installation:**
```bash
tesseract --version
```

### 5. Generate Sample PDFs (optional)
```bash
python generate_sample_pdfs.py
```
This creates `data/sample_pdfs/sbi_statement_jan2024.pdf` and `hdfc_statement_feb2024.pdf` for testing.

---

## ▶️ Running the Application

```bash
# Activate virtual environment (if not already)
venv\Scripts\activate

# Start Streamlit app
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 📖 Usage Guide

### 1. Upload Statement
- Navigate to **Upload Statement** in the sidebar
- Drag and drop one or more PDF bank statements
- Enter password if the PDF is password-protected
- Click **Process Statement(s)**

### 2. View Dashboard
- After processing, the **Dashboard** page shows:
  - KPI cards (total transactions, debits, credits, net flow)
  - Balance reconciliation status
  - Donut chart of category distribution
  - Debit vs. Credit bar chart
  - Spending by category

### 3. Review Transactions
- Navigate to **Transactions**
- Use search/filter to find specific transactions
- Review uncertain classifications
- Use the **Manual Category Override** editor to correct any transaction

### 4. Export Data
- Navigate to **Export**
- Download as Excel (3-sheet workbook) or CSV

### 5. Processing History
- Navigate to **History** to view previous sessions

### 6. Settings
- Add custom keyword classification rules
- Retrain the ML classifier
- Check system component status

---

## 📂 Sample Input & Output

### Sample Input
Two sample PDFs are generated by `generate_sample_pdfs.py`:

**SBI Statement (Jan 2024):**
- 15 transactions
- Categories: Salary, Food & Dining, Rent, ATM Withdrawal, Shopping, Utilities, Insurance, Investment, Interest, EMI/Loan, Transportation, Business, Education

**HDFC Statement (Feb 2024):**
- 15 transactions
- Similar variety of categories

### Sample Output (Excel)

| Sheet | Contents |
|-------|----------|
| Account Summary | Account holder, account number, IFSC, bank, period, balances, reconciliation |
| Transactions | Date, Description, Debit, Credit, Balance, Category, Confidence, Method |
| Category Summary | Category, Count, Total Debit, Total Credit, % of Total |

---

## 📤 Export Instructions

### Excel Export
1. Go to **Export** page
2. Click **⬇️ Download Excel**
3. File is downloaded as `bank_statement_YYYYMMDD_HHMMSS.xlsx`
4. Opens correctly in Microsoft Excel and Google Sheets
5. Contains colour-coded cells (coral for debits, mint for credits)
6. Auto-filter enabled on transaction table header

### CSV Export
1. Go to **Export** page
2. Click **⬇️ Download CSV**
3. UTF-8 encoded, compatible with Excel, Google Sheets, Python, R

---

## 🧪 Testing

Run the full test suite:
```bash
python -m pytest tests/ -v
```

**Test Results: 62/62 passing**

| Test File | Tests | Coverage |
|-----------|-------|----------|
| test_classification.py | 20 | Rule engine, ML classifier, hybrid engine |
| test_extraction.py | 25 | Date parsing, amount parsing, deduplication, normalisation, table parsing, account info |
| test_validation.py | 7 | Data validator, reconciliation |
| test_export.py | 9 | Excel export, CSV export |

Run specific test file:
```bash
python -m pytest tests/test_classification.py -v
```

---

## ⚠️ Limitations

1. **OCR Accuracy** — Tesseract accuracy depends on scan quality. Very poor quality scans may produce incorrect extractions.
2. **Bank Format Coverage** — The parser is tuned for common Indian bank formats. Unusual layouts may need custom rule additions.
3. **Training Data** — The ML classifier is trained on 58 synthetic samples. Accuracy improves with more labelled real-world data.
4. **Non-English Statements** — OCR and parsing are optimised for English text.
5. **Very Large PDFs** — PDFs with 100+ pages may take longer to process due to table detection overhead.
6. **Password-Protected PDFs** — The system can unlock single-password PDFs; certificate-based encryption is not supported.
7. **Multi-Currency** — Currently optimised for INR (₹). Multi-currency statements may have amount parsing issues.

---

## 🚀 Future Enhancements

1. **More Bank Parsers** — Dedicated parsers for each major bank's exact format
2. **Larger Training Dataset** — Collect and label 1000+ real transaction descriptions
3. **Budget Analysis** — Month-over-month spending trend charts
4. **Bank Statement Comparison** — Compare statements across multiple months
5. **REST API** — FastAPI backend for programmatic access
6. **Cloud Deployment** — Docker + Render/Railway deployment
7. **Multi-Language OCR** — Add Hindi and regional language support
8. **Email Integration** — Fetch e-statements directly from email
9. **UPI Transaction ID Parsing** — Extract UPI reference IDs from descriptions
10. **Tax Report Export** — Generate tax-relevant transaction summaries

---

## 👤 Author

Developed for the **Befree Automation Internship – Technical Assessment Round 2**

*Built with Python, Streamlit, pdfplumber, PyMuPDF, Tesseract, OpenCV, scikit-learn, and openpyxl.*
