"""
app.py – Bank Statement Processing & Classification System
Premium FinTech SaaS Streamlit Dashboard
"""
import io
import json
import logging
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

# ── Project root on path ──────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ROOT / "data" / "app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("app")

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="BankSight – Statement Processor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS – Premium FinTech Theme
# ═══════════════════════════════════════════════════════════════════════════════
CUSTOM_CSS = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── App background ── */
.stApp {
    background-color: #F5F7F4;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #172B36 0%, #1E3A47 100%);
    border-right: 1px solid #2D4A56;
}
[data-testid="stSidebar"] * {
    color: #E2EDF0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p {
    color: #B0CDD5 !important;
    font-size: 13px;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #78B9A7 !important;
}

/* ── Main content ── */
.main .block-container {
    padding: 1.5rem 2rem;
    max-width: 1400px;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(23,43,54,0.08);
    border: 1px solid #E8F0ED;
    transition: all 0.25s ease;
    margin-bottom: 12px;
}
.kpi-card:hover {
    box-shadow: 0 6px 24px rgba(58,141,133,0.15);
    transform: translateY(-2px);
}
.kpi-icon {
    font-size: 28px;
    margin-bottom: 8px;
    display: block;
}
.kpi-value {
    font-size: 26px;
    font-weight: 700;
    color: #24343B;
    line-height: 1.1;
}
.kpi-label {
    font-size: 12px;
    color: #718096;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
}
.kpi-credit .kpi-value { color: #3A8D85; }
.kpi-debit  .kpi-value { color: #D97770; }

/* ── Page title ── */
.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #24343B;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 14px;
    color: #718096;
    margin-bottom: 24px;
}

/* ── Section cards ── */
.section-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 10px rgba(23,43,54,0.07);
    border: 1px solid #E8F0ED;
    margin-bottom: 20px;
}

/* ── Upload zone ── */
.upload-zone {
    border: 2px dashed #78B9A7;
    border-radius: 14px;
    padding: 32px 24px;
    text-align: center;
    background: #F0F7F5;
    transition: all 0.2s ease;
}
.upload-zone:hover {
    border-color: #3A8D85;
    background: #E5F3F1;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3A8D85, #2A6E67) !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(58,141,133,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(58,141,133,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: white !important;
    color: #3A8D85 !important;
    border: 1.5px solid #3A8D85 !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #3A8D85, #78B9A7) !important;
    border-radius: 10px !important;
}
.stProgress {
    border-radius: 10px !important;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ── Alerts / info boxes ── */
.stAlert {
    border-radius: 10px !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 8px;
}
[data-testid="stTabs"] [role="tab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 500 !important;
    color: #718096 !important;
    background: #EAF0EC !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: #3A8D85 !important;
    color: white !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 10px rgba(23,43,54,0.07);
    border: 1px solid #E8F0ED;
}

/* ── Fade-in animation ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeInUp 0.4s ease both;
}

/* ── Skeleton loader ── */
@keyframes shimmer {
    0%   { background-position: -800px 0; }
    100% { background-position: 800px 0; }
}
.skeleton {
    background: linear-gradient(90deg, #E8F0ED 25%, #F5F7F4 50%, #E8F0ED 75%);
    background-size: 800px 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 10px;
    height: 80px;
    margin-bottom: 12px;
}

/* ── Processing step ── */
.step-active {
    color: #3A8D85;
    font-weight: 600;
}
.step-done {
    color: #5B9B78;
}
.step-pending {
    color: #CBD5E0;
}

/* ── Reconciliation banner ── */
.recon-ok {
    background: #EDFAF4;
    border-left: 4px solid #5B9B78;
    border-radius: 8px;
    padding: 12px 16px;
    color: #2D7A52;
    font-weight: 500;
}
.recon-warn {
    background: #FFF8EE;
    border-left: 4px solid #D9A86C;
    border-radius: 8px;
    padding: 12px 16px;
    color: #8A6020;
    font-weight: 500;
}

/* ── Hide Streamlit default decorations ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "processed": False,
        "transactions_df": pd.DataFrame(),
        "account_info": {},
        "reconciliation": {},
        "pdf_type": "unknown",
        "pages": 0,
        "warnings": [],
        "errors": [],
        "active_page": "Dashboard",
        "custom_categories": {},  # txn_index → user-chosen category
        "session_saved": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 24px 0;">
            <div style="font-size:40px;">🏦</div>
            <div style="font-size:18px; font-weight:700; color:#78B9A7; letter-spacing:0.5px;">
                BankSight
            </div>
            <div style="font-size:11px; color:#8EB5C0; margin-top:2px;">
                Statement Processing System
            </div>
        </div>
        <hr style="border:none; border-top:1px solid #2D4A56; margin:0 0 20px 0;">
        """, unsafe_allow_html=True)

        pages = {
            "📊 Dashboard": "Dashboard",
            "📤 Upload Statement": "Upload",
            "📋 Transactions": "Transactions",
            "📥 Export": "Export",
            "🕑 History": "History",
            "⚙️ Settings": "Settings",
        }

        for label, page_key in pages.items():
            is_active = st.session_state.active_page == page_key
            if st.button(
                label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_page = page_key
                st.rerun()

        st.markdown("<hr style='border:none; border-top:1px solid #2D4A56; margin:20px 0;'>",
                    unsafe_allow_html=True)

        # Quick stats in sidebar
        if st.session_state.processed and not st.session_state.transactions_df.empty:
            df = st.session_state.transactions_df
            st.markdown("**Quick Stats**")
            st.markdown(f"🔢 Transactions: **{len(df)}**")
            td = df["debit"].fillna(0).sum()
            tc = df["credit"].fillna(0).sum()
            st.markdown(f"🔴 Total Debit: **₹{td:,.0f}**")
            st.markdown(f"🟢 Total Credit: **₹{tc:,.0f}**")

        st.markdown("""
        <div style="position:absolute; bottom:20px; left:0; right:0; text-align:center;
                    font-size:10px; color:#4A6670;">
            Befree Automation Internship<br>Technical Assessment 2024
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: KPI CARD HTML
# ═══════════════════════════════════════════════════════════════════════════════
def kpi_card(icon: str, value: str, label: str, css_class: str = "") -> str:
    return f"""
    <div class="kpi-card {css_class}">
        <span class="kpi-icon">{icon}</span>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown('<div class="page-title">📊 Financial Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Overview of your processed bank statements</div>',
                unsafe_allow_html=True)

    if not st.session_state.processed or st.session_state.transactions_df.empty:
        # Welcome / empty state
        st.markdown("""
        <div style="background: linear-gradient(135deg, #172B36, #1E5050);
                    border-radius: 18px; padding: 48px 40px; text-align: center; color: white;
                    margin-bottom: 24px;">
            <div style="font-size:52px; margin-bottom:16px;">🏦</div>
            <h2 style="color:#78B9A7; margin-bottom:8px;">Welcome to BankSight</h2>
            <p style="color:#B0CDD5; font-size:15px; max-width:500px; margin:0 auto 24px;">
                Upload a bank statement PDF to get started. BankSight will automatically
                extract, classify, and analyse your transactions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("📄", "—", "Total Transactions"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("💸", "₹—", "Total Debits", "kpi-debit"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("💰", "₹—", "Total Credits", "kpi-credit"), unsafe_allow_html=True)

        st.info("👆 Navigate to **Upload Statement** in the sidebar to begin processing.")
        return

    df = st.session_state.transactions_df
    account = st.session_state.account_info
    recon = st.session_state.reconciliation

    # ── KPI Row 1 ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    total_txns = len(df)
    total_debit = df["debit"].fillna(0).sum()
    total_credit = df["credit"].fillna(0).sum()
    categorised = (df.get("category", pd.Series()) != "Other / Uncategorized").sum() if "category" in df.columns else 0
    uncategorised = total_txns - categorised

    with c1:
        st.markdown(kpi_card("🔢", f"{total_txns:,}", "Total Transactions"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("💸", f"₹{total_debit:,.2f}", "Total Debits", "kpi-debit"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("💰", f"₹{total_credit:,.2f}", "Total Credits", "kpi-credit"), unsafe_allow_html=True)
    with c4:
        net = total_credit - total_debit
        cls = "kpi-credit" if net >= 0 else "kpi-debit"
        st.markdown(kpi_card("📈", f"₹{net:,.2f}", "Net Cash Flow", cls), unsafe_allow_html=True)

    # ── KPI Row 2 ──────────────────────────────────────────────────────────────
    c5, c6, c7, c8 = st.columns(4)
    ob = account.get("opening_balance", "N/A")
    cb = account.get("closing_balance", "N/A")
    with c5:
        st.markdown(kpi_card("🏦", f"₹{float(ob):,.2f}" if ob and ob != "N/A" else "N/A",
                             "Opening Balance"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("🏁", f"₹{float(cb):,.2f}" if cb and cb != "N/A" else "N/A",
                             "Closing Balance"), unsafe_allow_html=True)
    with c7:
        st.markdown(kpi_card("✅", f"{categorised}", "Categorised"), unsafe_allow_html=True)
    with c8:
        st.markdown(kpi_card("❓", f"{uncategorised}", "Uncategorised"), unsafe_allow_html=True)

    # ── Reconciliation Banner ──────────────────────────────────────────────────
    if recon.get("status") == "ok":
        st.markdown(f'<div class="recon-ok">✅ {recon.get("message","")}</div>', unsafe_allow_html=True)
    elif recon.get("status") == "warning":
        st.markdown(f'<div class="recon-warn">⚠️ {recon.get("message","")}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    if "category" in df.columns:
        import plotly.express as px
        import plotly.graph_objects as go

        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**Transaction Category Distribution**")

            cat_counts = df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]

            # Load colours
            try:
                with open(ROOT / "config" / "categories.json") as f:
                    cat_config = json.load(f)
                color_map = cat_config.get("category_colors", {})
                colors = [color_map.get(c, "#78B9A7") for c in cat_counts["Category"]]
            except Exception:
                colors = None

            fig_donut = go.Figure(go.Pie(
                labels=cat_counts["Category"],
                values=cat_counts["Count"],
                hole=0.55,
                marker_colors=colors,
                textinfo="percent+label",
                textfont_size=11,
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
            ))
            fig_donut.update_layout(
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                height=300,
            )
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**Debit vs Credit**")

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name="Debit",
                x=["Debit"],
                y=[total_debit],
                marker_color="#D97770",
                width=0.4,
            ))
            fig_bar.add_trace(go.Bar(
                name="Credit",
                x=["Credit"],
                y=[total_credit],
                marker_color="#3A8D85",
                width=0.4,
            ))
            fig_bar.update_layout(
                showlegend=True,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300,
                yaxis=dict(tickprefix="₹", gridcolor="#E8F0ED"),
                xaxis=dict(showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                bargap=0.3,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Category spend bar chart
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Spending by Category**")

        cat_debit = (
            df.groupby("category")["debit"]
            .sum()
            .fillna(0)
            .reset_index()
            .sort_values("debit", ascending=True)
        )
        cat_debit = cat_debit[cat_debit["debit"] > 0]

        if not cat_debit.empty:
            try:
                cat_colors_list = [color_map.get(c, "#78B9A7") for c in cat_debit["category"]]
            except Exception:
                cat_colors_list = "#3A8D85"

            fig_hbar = go.Figure(go.Bar(
                x=cat_debit["debit"],
                y=cat_debit["category"],
                orientation="h",
                marker_color=cat_colors_list,
                hovertemplate="<b>%{y}</b><br>₹%{x:,.2f}<extra></extra>",
            ))
            fig_hbar.update_layout(
                margin=dict(t=10, b=10, l=10, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=max(200, len(cat_debit) * 32),
                xaxis=dict(tickprefix="₹", gridcolor="#E8F0ED"),
                yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_hbar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD
# ═══════════════════════════════════════════════════════════════════════════════
def page_upload():
    st.markdown('<div class="page-title">📤 Upload Bank Statement</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Upload one or more PDF bank statements for processing</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop PDF bank statement(s) here",
        type=["pdf"],
        accept_multiple_files=True,
        help="Supported: Text-based and scanned (image) PDFs up to 50 MB each",
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        for uf in uploaded_files:
            size_mb = uf.size / (1024 * 1024)
            st.markdown(f"- 📄 `{uf.name}` — {size_mb:.2f} MB")

    password = st.text_input(
        "Password (if PDF is password-protected)",
        type="password",
        placeholder="Leave blank if not required",
    )

    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        col_btn, col_reset = st.columns([2, 1])
        with col_btn:
            process_clicked = st.button("⚡ Process Statement(s)", type="primary", use_container_width=True)
        with col_reset:
            if st.button("🔄 Reset", type="secondary", use_container_width=True):
                for key in ["processed", "transactions_df", "account_info",
                            "reconciliation", "warnings", "errors"]:
                    st.session_state[key] = (
                        pd.DataFrame() if key == "transactions_df"
                        else {} if key in ("account_info", "reconciliation")
                        else [] if key in ("warnings", "errors")
                        else False
                    )
                st.rerun()

        if process_clicked:
            _run_processing(uploaded_files, password or None)


def _run_processing(uploaded_files, password):
    """Run the full processing pipeline with animated progress."""
    from modules.bank_parser import process_pdf
    from modules.classification_engine import ClassificationEngine
    from modules.data_validator import validate_transactions, validate_amounts
    from modules.reconciliation import reconcile
    from modules.database import save_session

    steps = [
        "📂 Validating PDF...",
        "🔍 Detecting statement format...",
        "📄 Extracting transaction data...",
        "🖼️ Processing OCR (if required)...",
        "🧹 Cleaning & validating transactions...",
        "🏷️ Classifying transactions...",
        "📊 Generating financial summary...",
        "💾 Saving to history...",
    ]

    progress_bar = st.progress(0, text=steps[0])
    status_area = st.empty()

    all_dfs = []
    all_warnings = []
    final_account_info = {}
    final_pdf_type = "text"
    final_pages = 0

    try:
        engine = ClassificationEngine()

        for file_idx, uf in enumerate(uploaded_files):
            # Save uploaded file to temp path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uf.read())
                tmp_path = tmp.name

            def _progress(step_msg, pct):
                overall = int((file_idx / len(uploaded_files)) * 100 + pct / len(uploaded_files))
                progress_bar.progress(min(overall, 95), text=f"[{uf.name}] {step_msg}")

            # Step 1-4: Extraction
            status_area.info(f"Processing `{uf.name}`…")
            result = process_pdf(tmp_path, password=password, progress_callback=_progress)

            os.unlink(tmp_path)

            if result["errors"]:
                for err in result["errors"]:
                    st.error(f"❌ `{uf.name}`: {err}")
                continue

            all_warnings.extend(result["warnings"])
            final_account_info = result["account_info"]
            final_pdf_type = result["pdf_type"]
            final_pages += result["pages"]
            df = result["transactions"]

            if df.empty:
                st.warning(f"⚠️ No transactions extracted from `{uf.name}`.")
                continue

            # Step 5: Validate
            progress_bar.progress(60, text=steps[4])
            df, val_warnings = validate_transactions(df)
            all_warnings.extend(val_warnings)

            # Step 6: Classify
            progress_bar.progress(70, text=steps[5])
            df = engine.classify_dataframe(df)

            all_dfs.append(df)

        # Merge all DataFrames
        progress_bar.progress(85, text=steps[6])
        if all_dfs:
            merged_df = pd.concat(all_dfs, ignore_index=True)
            merged_df = merged_df.sort_values("date").reset_index(drop=True)
        else:
            merged_df = pd.DataFrame()

        # Reconcile
        recon = reconcile(merged_df, final_account_info) if not merged_df.empty else {}

        # Step 8: Save to history
        progress_bar.progress(92, text=steps[7])
        if not merged_df.empty:
            try:
                save_session(
                    filename=", ".join(f.name for f in uploaded_files),
                    pdf_type=final_pdf_type,
                    pages=final_pages,
                    df=merged_df,
                    account_info=final_account_info,
                    reconciliation=recon,
                    warnings=all_warnings,
                )
            except Exception as e:
                logger.warning("Could not save to history DB: %s", e)

        # Persist to session state
        progress_bar.progress(100, text="✅ Complete!")
        st.session_state.processed = True
        st.session_state.transactions_df = merged_df
        st.session_state.account_info = final_account_info
        st.session_state.reconciliation = recon
        st.session_state.pdf_type = final_pdf_type
        st.session_state.pages = final_pages
        st.session_state.warnings = all_warnings
        st.session_state.custom_categories = {}

        status_area.empty()

        if merged_df.empty:
            st.error("❌ No transactions could be extracted from the uploaded file(s).")
        else:
            st.success(f"✅ Successfully processed {len(merged_df)} transactions from {len(uploaded_files)} file(s)!")
            if all_warnings:
                with st.expander(f"⚠️ {len(all_warnings)} Warning(s)", expanded=False):
                    for w in all_warnings:
                        st.warning(w)
            time.sleep(1)
            st.session_state.active_page = "Dashboard"
            st.rerun()

    except Exception as exc:
        logger.error("Processing failed: %s", exc, exc_info=True)
        st.error(f"❌ An unexpected error occurred: {exc}")
        progress_bar.empty()
        status_area.empty()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def page_transactions():
    st.markdown('<div class="page-title">📋 Transaction Results</div>', unsafe_allow_html=True)

    if not st.session_state.processed or st.session_state.transactions_df.empty:
        st.info("No transactions loaded. Please upload and process a statement first.")
        return

    df = st.session_state.transactions_df.copy()

    # Apply user manual overrides
    if st.session_state.custom_categories:
        for idx, cat in st.session_state.custom_categories.items():
            if idx in df.index:
                df.at[idx, "category"] = cat
                df.at[idx, "classification_method"] = "manual"
                df.at[idx, "confidence"] = 1.0

    # ── Filter Controls ────────────────────────────────────────────────────────
    with st.expander("🔎 Filter & Search", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)

        with fc1:
            search_q = st.text_input("Search description", placeholder="e.g. SWIGGY, SALARY…")
        with fc2:
            categories = ["All"] + sorted(df["category"].unique().tolist()) if "category" in df.columns else ["All"]
            cat_filter = st.selectbox("Category", categories)
        with fc3:
            txn_type = st.selectbox("Transaction Type", ["All", "Debit only", "Credit only"])
        with fc4:
            if "date" in df.columns:
                try:
                    min_d = pd.to_datetime(df["date"]).min().date()
                    max_d = pd.to_datetime(df["date"]).max().date()
                    date_range = st.date_input("Date Range", value=(min_d, max_d))
                except Exception:
                    date_range = None
            else:
                date_range = None

    # Apply filters
    filtered = df.copy()
    if search_q:
        filtered = filtered[filtered["description"].str.contains(search_q, case=False, na=False)]
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if txn_type == "Debit only":
        filtered = filtered[filtered["debit"].notna() & (filtered["debit"] > 0)]
    elif txn_type == "Credit only":
        filtered = filtered[filtered["credit"].notna() & (filtered["credit"] > 0)]
    if date_range and len(date_range) == 2:
        try:
            filtered = filtered[
                (pd.to_datetime(filtered["date"]) >= pd.Timestamp(date_range[0])) &
                (pd.to_datetime(filtered["date"]) <= pd.Timestamp(date_range[1]))
            ]
        except Exception:
            pass

    st.markdown(f"**{len(filtered)} of {len(df)} transactions shown**")

    # ── Category Summary Chips ─────────────────────────────────────────────────
    if "category" in filtered.columns:
        cat_counts = filtered["category"].value_counts()
        chips_html = " ".join(
            f'<span style="background:#EAF0EC; color:#172B36; border-radius:20px; '
            f'padding:3px 10px; font-size:12px; margin:2px; display:inline-block;">'
            f'{c} <b>{n}</b></span>'
            for c, n in cat_counts.items()
        )
        st.markdown(chips_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Transaction Table ──────────────────────────────────────────────────────
    display_cols = [c for c in
                    ["date", "description", "debit", "credit", "balance",
                     "category", "confidence", "classification_method"]
                    if c in filtered.columns]

    styled_df = filtered[display_cols].copy()
    for col in ["debit", "credit", "balance"]:
        if col in styled_df.columns:
            styled_df[col] = styled_df[col].apply(
                lambda x: f"₹{x:,.2f}" if pd.notna(x) and x != "" else ""
            )

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=min(600, 40 + len(filtered) * 36),
        column_config={
            "date": st.column_config.TextColumn("Date", width=120),
            "description": st.column_config.TextColumn("Description", width=350),
            "debit": st.column_config.TextColumn("Debit", width=120),
            "credit": st.column_config.TextColumn("Credit", width=120),
            "balance": st.column_config.TextColumn("Balance", width=120),
            "category": st.column_config.TextColumn("Category", width=180),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f", width=100),
            "classification_method": st.column_config.TextColumn("Method", width=120),
        },
        hide_index=True,
    )

    # ── Manual Category Editor ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ✏️ Manual Category Override")
    st.markdown("Correct the category for any transaction:")

    with st.expander("Show manual editor", expanded=False):
        try:
            with open(ROOT / "config" / "categories.json") as f:
                all_cats = json.load(f)["categories"]
        except Exception:
            all_cats = ["Salary", "Food & Dining", "Shopping", "Other / Uncategorized"]

        col_sel, col_cat, col_apply = st.columns([2, 2, 1])
        with col_sel:
            uncategorised_df = filtered[filtered.get("category", pd.Series()) == "Other / Uncategorized"] if "category" in filtered.columns else filtered
            row_options = {
                f"[{r['date']}] {str(r['description'])[:50]}": idx
                for idx, r in uncategorised_df.iterrows()
            }
            if row_options:
                selected_label = st.selectbox("Select transaction", list(row_options.keys()))
                selected_idx = row_options[selected_label]
            else:
                selected_label = None
                selected_idx = None
                st.info("No uncategorised transactions.")

        with col_cat:
            new_cat = st.selectbox("New category", all_cats)

        with col_apply:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Apply", type="primary") and selected_idx is not None:
                st.session_state.custom_categories[selected_idx] = new_cat
                st.session_state.transactions_df.at[selected_idx, "category"] = new_cat
                st.session_state.transactions_df.at[selected_idx, "classification_method"] = "manual"
                st.session_state.transactions_df.at[selected_idx, "confidence"] = 1.0
                st.success(f"✅ Updated category to **{new_cat}**")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: EXPORT
# ═══════════════════════════════════════════════════════════════════════════════
def page_export():
    st.markdown('<div class="page-title">📥 Export Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Download your processed statements in Excel or CSV format</div>',
                unsafe_allow_html=True)

    if not st.session_state.processed or st.session_state.transactions_df.empty:
        st.info("No data to export. Please process a bank statement first.")
        return

    df = st.session_state.transactions_df
    account = st.session_state.account_info
    recon = st.session_state.reconciliation

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f"**Ready to export {len(df)} transactions**")
    st.markdown(f"- Account: `{account.get('account_holder', 'N/A')}`")
    st.markdown(f"- Bank: `{account.get('bank_name', 'N/A')}`")
    st.markdown(f"- Period: `{account.get('statement_period', 'N/A')}`")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Excel Export (.xlsx)")
        st.markdown("""
        Professional workbook with:
        - **Account Summary** sheet
        - **Transactions** sheet (colour-coded, filtered)
        - **Category Summary** sheet
        - Formatted columns, freeze panes, auto-filter
        """)
        with st.spinner("Preparing Excel file…"):
            try:
                from modules.export_handler import export_to_excel
                xlsx_bytes = export_to_excel(df, account, recon)
                st.download_button(
                    label="⬇️ Download Excel",
                    data=xlsx_bytes,
                    file_name=f"bank_statement_{_safe_filename()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Excel generation failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 📄 CSV Export (.csv)")
        st.markdown("""
        Flat structured CSV containing:
        - Date, Description, Debit, Credit, Balance
        - Category, Confidence, Classification Method
        - Compatible with Excel, Google Sheets
        """)
        try:
            from modules.export_handler import export_to_csv
            csv_str = export_to_csv(df)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_str.encode("utf-8"),
                file_name=f"bank_statement_{_safe_filename()}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"CSV generation failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


def _safe_filename():
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
def page_history():
    st.markdown('<div class="page-title">🕑 Processing History</div>', unsafe_allow_html=True)

    try:
        from modules.database import get_sessions, get_session_transactions
        sessions = get_sessions()
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    if not sessions:
        st.info("No processing history yet. Process a statement to see it here.")
        return

    for sess in sessions[:20]:
        with st.expander(
            f"📄 {sess['filename']} — {sess['processed_at'][:16].replace('T', ' ')} "
            f"| {sess['transaction_count']} transactions",
            expanded=False,
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Bank:** {sess.get('bank_name','N/A')}")
                st.markdown(f"**Account Holder:** {sess.get('account_holder','N/A')}")
            with c2:
                st.markdown(f"**PDF Type:** {sess.get('pdf_type','N/A')}")
                st.markdown(f"**Pages:** {sess.get('pages','N/A')}")
            with c3:
                st.markdown(f"**Total Debits:** ₹{(sess.get('total_debits') or 0):,.2f}")
                st.markdown(f"**Total Credits:** ₹{(sess.get('total_credits') or 0):,.2f}")

            if st.button("Load Transactions", key=f"load_{sess['id']}"):
                hist_df = get_session_transactions(sess["id"])
                st.dataframe(hist_df, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
def page_settings():
    st.markdown('<div class="page-title">⚙️ Settings</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🏷️ Custom Classification Rules")
    st.markdown("Add a keyword rule to automatically classify future transactions.")

    try:
        with open(ROOT / "config" / "categories.json") as f:
            all_cats = json.load(f)["categories"]
    except Exception:
        all_cats = ["Other / Uncategorized"]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        rule_cat = st.selectbox("Target Category", all_cats)
    with col2:
        rule_kw = st.text_input("Keywords (comma-separated)", placeholder="e.g. netflix, spotify")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Rule", type="primary"):
            if rule_kw.strip():
                keywords = [k.strip().lower() for k in rule_kw.split(",") if k.strip()]
                if "custom_rules" not in st.session_state:
                    st.session_state.custom_rules = []
                st.session_state.custom_rules.append({"category": rule_cat, "keywords": keywords})
                st.success(f"✅ Rule added for **{rule_cat}** with {len(keywords)} keyword(s).")
            else:
                st.warning("Please enter at least one keyword.")

    if "custom_rules" in st.session_state and st.session_state.custom_rules:
        st.markdown("**Current custom rules:**")
        for i, rule in enumerate(st.session_state.custom_rules):
            st.markdown(f"- **{rule['category']}**: `{', '.join(rule['keywords'])}`")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### ℹ️ System Information")

    # Check OCR availability
    try:
        from modules.ocr_engine import is_tesseract_available
        ocr_ok = is_tesseract_available()
    except Exception:
        ocr_ok = False

    try:
        from modules.ml_classifier import MLClassifier
        ml = MLClassifier()
        ml_ok = ml.is_trained
    except Exception:
        ml_ok = False

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Tesseract OCR:** {'✅ Available' if ocr_ok else '⚠️ Not found'}")
    with c2:
        st.markdown(f"**ML Classifier:** {'✅ Trained' if ml_ok else '⚠️ Not trained'}")
    with c3:
        st.markdown("**DB:** ✅ SQLite")

    if not ocr_ok:
        st.warning(
            "Tesseract OCR is not installed. Scanned PDFs will use text-extraction fallback. "
            "Install from: https://github.com/UB-Mannheim/tesseract/wiki"
        )

    if not ml_ok:
        if st.button("🔄 Train ML Classifier Now"):
            with st.spinner("Training…"):
                try:
                    from modules.ml_classifier import MLClassifier
                    m = MLClassifier()
                    m.retrain()
                    st.success("✅ ML classifier trained successfully!")
                except Exception as e:
                    st.error(f"Training failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    render_sidebar()

    page = st.session_state.active_page
    if page == "Dashboard":
        page_dashboard()
    elif page == "Upload":
        page_upload()
    elif page == "Transactions":
        page_transactions()
    elif page == "Export":
        page_export()
    elif page == "History":
        page_history()
    elif page == "Settings":
        page_settings()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
