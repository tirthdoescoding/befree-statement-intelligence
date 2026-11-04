"""
server.py – Production-grade FastAPI backend wrapping the bank statement processing pipeline.
Preserves all processing, OCR, non-LLM hybrid classification, reconciliation, and export logic.
"""
import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from modules.bank_parser import process_pdf
from modules.classification_engine import ClassificationEngine
from modules.data_validator import validate_amounts, validate_transactions
from modules.database import get_session_transactions, get_sessions, init_db, save_session
from modules.export_handler import export_to_csv, export_to_excel
from modules.reconciliation import reconcile

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Befree Statement Intelligence API",
    description="High-performance Non-LLM Bank Statement Extraction & Classification API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ClassificationEngine()
init_db()


class CategoryUpdateRequest(BaseModel):
    category: str


class CustomRuleRequest(BaseModel):
    category: str
    keywords: List[str]


@app.get("/api/health")
def health_check():
    from modules.ocr_engine import is_tesseract_available

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ocr_available": is_tesseract_available(),
        "ml_trained": engine.ml_classifier.is_trained,
    }


@app.get("/api/categories")
def get_categories():
    cfg_path = Path(__file__).parent / "config" / "categories.json"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "categories": [
            "Salary",
            "Food & Dining",
            "Shopping",
            "Rent",
            "Utilities",
            "Healthcare",
            "Transportation",
            "ATM Withdrawal",
            "Bank Charges",
            "EMI / Loan",
            "Investment",
            "Insurance",
            "Education",
            "Transfers",
            "Business Transactions",
            "Interest",
            "Other / Uncategorized",
        ]
    }


@app.post("/api/process")
async def process_statements(
    files: List[UploadFile] = File(...),
    password: Optional[str] = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    all_dfs = []
    combined_warnings = []
    account_info = {}
    primary_pdf_type = "text"
    total_pages = 0
    file_names = [f.filename for f in files]

    temp_dir = tempfile.mkdtemp()
    try:
        for f in files:
            file_path = os.path.join(temp_dir, f.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)

            res = process_pdf(file_path, password=password)

            if res.get("errors"):
                combined_warnings.extend(res["errors"])
                continue

            combined_warnings.extend(res.get("warnings", []))
            total_pages += res.get("pages", 0)
            if res.get("pdf_type"):
                primary_pdf_type = res["pdf_type"]

            if not account_info and res.get("account_info"):
                account_info = res["account_info"]
            elif res.get("account_info"):
                for k, v in res["account_info"].items():
                    if v and not account_info.get(k):
                        account_info[k] = v

            df = res.get("transactions", pd.DataFrame())
            if not df.empty:
                df, val_warn = validate_transactions(df)
                combined_warnings.extend(val_warn)
                df = engine.classify_dataframe(df)
                all_dfs.append(df)

        if not all_dfs:
            return {
                "success": False,
                "message": "No transactions could be extracted from provided file(s).",
                "warnings": combined_warnings,
                "account_info": account_info,
                "transactions": [],
                "analytics": {},
                "reconciliation": {},
            }

        merged_df = pd.concat(all_dfs, ignore_index=True)
        merged_df = merged_df.sort_values("date").reset_index(drop=True)
        merged_df["id"] = range(1, len(merged_df) + 1)

        recon = reconcile(merged_df, account_info)

        # Save to SQLite History
        session_id = None
        try:
            session_id = save_session(
                filename=", ".join(file_names),
                pdf_type=primary_pdf_type,
                pages=total_pages,
                df=merged_df,
                account_info=account_info,
                reconciliation=recon,
                warnings=combined_warnings,
            )
        except Exception as e:
            logger.warning(f"Failed to persist session to DB: {e}")

        # Compute High-level Analytics
        total_txns = len(merged_df)
        total_debit = float(merged_df["debit"].fillna(0).sum())
        total_credit = float(merged_df["credit"].fillna(0).sum())
        net_flow = total_credit - total_debit

        cat_breakdown = (
            merged_df.groupby("category")
            .agg(
                count=("description", "count"),
                debit=("debit", "sum"),
                credit=("credit", "sum"),
            )
            .reset_index()
            .to_dict(orient="records")
        )

        # Monthly Trends
        merged_df["month"] = pd.to_datetime(merged_df["date"], errors="coerce").dt.strftime("%b %Y")
        monthly_trends = (
            merged_df.groupby("month")
            .agg(
                debit=("debit", "sum"),
                credit=("credit", "sum"),
                count=("description", "count"),
            )
            .reset_index()
            .to_dict(orient="records")
        )

        # Replace NaN with None for JSON serialization
        merged_df = merged_df.fillna(value=None).replace([float('nan')], [None])
        records = []
        for r in merged_df.to_dict(orient="records"):
            clean_r = {}
            for k, v in r.items():
                if pd.isna(v) or v != v:
                    clean_r[k] = None
                else:
                    clean_r[k] = v
            records.append(clean_r)

        return {
            "success": True,
            "session_id": session_id,
            "filename": ", ".join(file_names),
            "pdf_type": primary_pdf_type,
            "pages": total_pages,
            "account_info": account_info,
            "reconciliation": recon,
            "warnings": combined_warnings,
            "transactions": records,
            "analytics": {
                "total_transactions": total_txns,
                "total_debit": round(total_debit, 2),
                "total_credit": round(total_credit, 2),
                "net_flow": round(net_flow, 2),
                "category_breakdown": cat_breakdown,
                "monthly_trends": monthly_trends,
            },
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


class ExportRequest(BaseModel):
    transactions: List[Dict]
    account_info: Dict
    reconciliation: Dict


@app.post("/api/export/excel")
def export_excel(payload: ExportRequest):
    df = pd.DataFrame(payload.transactions)
    if "id" in df.columns:
        df = df.drop(columns=["id"])
    excel_bytes = export_to_excel(df, payload.account_info, payload.reconciliation)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=statement_export.xlsx"},
    )


@app.post("/api/export/csv")
def export_csv(payload: ExportRequest):
    df = pd.DataFrame(payload.transactions)
    if "id" in df.columns:
        df = df.drop(columns=["id"])
    csv_str = export_to_csv(df)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=statement_export.csv"},
    )


@app.get("/api/history")
def get_history_sessions():
    sessions = get_sessions()
    return {"sessions": sessions}


@app.get("/api/history/{session_id}")
def get_history_detail(session_id: int):
    df = get_session_transactions(session_id)
    records = df.where(pd.notnull(df), None).to_dict(orient="records")
    return {"transactions": records}


@app.get("/api/sample-files")
def get_sample_files():
    sample_dir = Path(__file__).parent / "data" / "sample_pdfs"
    files = []
    if sample_dir.exists():
        for p in sample_dir.glob("*.pdf"):
            files.append({"name": p.name, "path": str(p), "size_kb": round(p.stat().st_size / 1024, 1)})
    return {"samples": files}


@app.get("/api/sample-files/download/{filename}")
def download_sample_file(filename: str):
    file_path = Path(__file__).parent / "data" / "sample_pdfs" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample file not found")
    return FileResponse(path=str(file_path), filename=filename, media_type="application/pdf")
