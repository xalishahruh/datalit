import streamlit as st
import pandas as pd
import json
from io import BytesIO
from utils.ui_utils import apply_custom_styles

st.set_page_config(page_title="Export Results", layout="wide")
apply_custom_styles()

st.title("📤 Export Results")

if "working_df" not in st.session_state or st.session_state.working_df is None:
    st.warning("Please upload a dataset first!")
    st.stop()

df = st.session_state.working_df
log = st.session_state.recipe_log

col_data, col_log = st.columns([1, 1])

with col_data:
    st.subheader("💾 Export Cleaned Dataset")
    
    # CSV Export
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name="datalit_cleaned_data.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Excel Export
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Download Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name="datalit_cleaned_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_log:
    st.subheader("📜 Transformation Recipe")
    
    if not log:
        st.info("No transformations applied yet.")
    else:
        # JSON Recipe Export
        recipe_json = json.dumps(log, indent=4)
        st.download_button(
            label="📥 Download Recipe (JSON)",
            data=recipe_json,
            file_name="datalit_recipe.json",
            mime="application/json",
            use_container_width=True
        )
        
        # Display log entries
        for i, entry in enumerate(log):
            with st.expander(f"Step {i+1}: {entry['operation']}"):
                st.write(f"**Timestamp:** {entry['timestamp']}")
                st.write(f"**Affected Columns:** {entry['affected_columns']}")
                st.json(entry['parameters'])

st.divider()
st.subheader("Final Preview")
st.dataframe(df.head(50), use_container_width=True)
