import streamlit as st
import pandas as pd
import json
import io
import datetime
from services.dataset_manager import get_dataset, dataset_exists, init_manager
from services import export_service
from utils.ui_utils import apply_custom_styles

st.set_page_config(page_title="Export Hub", layout="wide")
apply_custom_styles()

# Initialize session state
init_manager()

st.title("💼 DataLit Export Hub")
st.markdown("---")

if not dataset_exists():
    st.warning("⚠️ Please upload a dataset first in the Data Upload page.")
    st.stop()

df = get_dataset()
recipe_log = st.session_state.get("recipe_log", [])

# --- Section 1: Detailed Audit Trail ---
with st.expander("📜 Transformation History & Audit Trail", expanded=False):
    if not recipe_log:
        st.info("No transformations applied yet. Your dataset is in its original state.")
    else:
        summary_data = []
        for step_num, log in enumerate(recipe_log, 1):
            param_summary = ", ".join([f"{k}={v}" for k, v in log.get('parameters', {}).items()])
            cols_summary = ", ".join(log.get('affected_columns', []))
            summary_data.append({
                "Step": step_num,
                "Operation": log.get('operation', 'Unknown'),
                "Affected Columns": cols_summary,
                "Parameters": param_summary,
                "Time": log.get('timestamp', '')
            })
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

# --- Section 2: Data & Report Export ---
st.subheader("📥 Multi-Format Export Center")
st.write("Generate and download your cleaned data and reports in various formats.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("📊 **Standard CSV**")
    csv_bytes = export_service.export_as_csv(df)
    st.download_button(
        "Download CSV", csv_bytes, 
        f"clean_data_{datetime.datetime.now().strftime('%Y%m%d')}.csv", 
        "text/csv", use_container_width=True
    )

with col2:
    st.info("🔗 **JSON Data**")
    json_bytes = export_service.export_as_json(df)
    st.download_button(
        "Download JSON", json_bytes, 
        f"data_export_{datetime.datetime.now().strftime('%Y%m%d')}.json", 
        "application/json", use_container_width=True
    )

with col3:
    st.info("📑 **Excel Worksheet**")
    excel_bytes = export_service.export_as_excel(df)
    st.download_button(
        "Download Excel", excel_bytes,
        f"clean_data_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col4:
    st.info("📋 **PDF Summary**")
    if st.button("Generate PDF", use_container_width=True):
        summary_text = f"Dataset size: {df.shape}\nColumns: {', '.join(df.columns)}\nRows: {len(df)}"
        pdf_bytes = export_service.generate_pdf_report(summary_text)
        st.download_button("Download PDF", pdf_bytes, "summary_report.pdf", "application/pdf", use_container_width=True)

# --- Section 3: Production Pipeline ---
st.markdown("---")
col_p1, col_p2 = st.columns([2, 1])
with col_p1:
    st.subheader("🐍 Production Pipeline")
    st.write("Export a standalone Python script that reproduces all these steps on new data.")
with col_p2:
    python_code = export_service.generate_python_script(recipe_log)
    st.download_button(
        "Download .py Script", python_code, 
        "transformation_pipeline.py", 
        "text/x-python", use_container_width=True, type="primary"
    )

# --- Section 3: Visual Audit (Phase 4 Continuation) ---
st.markdown("---")
st.subheader("🖼️ Visualization Archive")
if 'fig' in st.session_state:
    st.write("Download the latest visualization generated in the Builder.")
    st.pyplot(st.session_state.fig)
    img_bytes = export_service.export_as_image(st.session_state.fig)
    st.download_button("Download High-Res PNG", img_bytes, "viz_export.png", "image/png", use_container_width=True)
else:
    st.info("No visualizations currently in session. Go to the **Visualization Builder** to create one.")

# Business Alignment Footer
st.markdown("---")
st.caption("DataLit Export Module v2.0 | Optimized for Business Intelligence & Reproducibility")