import streamlit as st
import pandas as pd
import json
import io
import datetime
from services.dataset_manager import get_dataset, dataset_exists
from utils.ui_utils import apply_custom_styles

st.set_page_config(page_title="Export Results", layout="wide")
apply_custom_styles()

st.title("💾 Export Results & Transformation Log")
st.markdown("---")

if not dataset_exists():
    st.warning("⚠️ Please upload a dataset first in the Data Upload page.")
    st.stop()

df = get_dataset()
recipe_log = st.session_state.get("recipe_log", [])

# --- Section 1: Transformation Log UI ---
st.subheader("📜 Transformation History")

if not recipe_log:
    st.info("No transformations applied yet. Your dataset is in its original state.")
else:
    # Build a summary DataFrame for the top-level View
    summary_data = []
    for step_num, log in enumerate(recipe_log, 1):
        # Flatten parameters for summary view
        param_summary = ", ".join([f"{k}={v}" for k, v in log.get('parameters', {}).items()])
        cols_summary = ", ".join(log.get('affected_columns', []))
        
        summary_data.append({
            "Step": step_num,
            "Operation": log.get('operation', 'Unknown'),
            "Affected Columns": cols_summary,
            "Parameters": param_summary,
            "Time": log.get('timestamp', '')
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # Build the Detailed Audit Trail
    st.markdown("#### Detailed Recipe Audit")
    for step_num, log in enumerate(recipe_log, 1):
        with st.expander(f"Step {step_num}: {log.get('operation')} at {log.get('timestamp')}"):
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Affected Columns:**")
                st.write(log.get("affected_columns"))
            with cols[1]:
                st.markdown("**Parameters (JSON):**")
                st.json(log.get("parameters", {}))


# --- Section 2: Data Export Panel ---
st.markdown("---")
st.subheader("📥 Export Downloads")

col1, col2, col3 = st.columns(3)

# 1. CSV Download
with col1:
    st.markdown("#### The Cleaned Data")
    st.write("Download your perfectly prepped dataset as a standard CSV.")
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=f"datalit_cleaned_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# 2. Excel Download
with col2:
    st.markdown("#### Excel Format")
    st.write("Download your dataset structured for Excel (.xlsx).")
    
    # Write to a buffer using openpyxl
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cleaned Data')
    excel_bytes = buffer.getvalue()
    
    st.download_button(
        label="Download Excel",
        data=excel_bytes,
        file_name=f"datalit_cleaned_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# 3. JSON Recipe Download
with col3:
    st.markdown("#### Transformation Recipe")
    st.write("Download the exact JSON log of operations for automated reproducibility.")
    recipe_json = json.dumps(recipe_log, indent=4)
    st.download_button(
        label="Download JSON Recipe",
        data=recipe_json,
        file_name=f"datalit_recipe_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )