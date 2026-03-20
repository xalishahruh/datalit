import streamlit as st

st.set_page_config(page_title="Data Upload & Overview", layout="wide")
from utils.ui_utils import apply_custom_styles
apply_custom_styles()

from core.loader import load_dataset
from core.profiling import (
    infer_dtypes,
    missing_values,
    duplicate_count,
    numeric_summary,
    categorical_summary
)
from services.dataset_manager import (
    store_dataset,
    get_dataset,
    dataset_exists,
    init_manager,
    reset_session
)

# 1. Initialize state
init_manager()

st.title("📂 Data Upload & Overview")

# 2. Upload Section
uploaded_file = st.file_uploader(
    "Upload your dataset (CSV, Excel, or JSON)",
    type=["csv", "xlsx", "json"],
    key=f"uploader_{st.session_state.get('uploader_key', 0)}"
)

if uploaded_file is not None:
    try:
        file_type = uploaded_file.name.split(".")[-1]
        df = load_dataset(uploaded_file, file_type)
        store_dataset(df)
        st.success(f"Successfully loaded '{uploaded_file.name}'")
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")

# 3. Overview Section (Visible only if data is loaded)
if dataset_exists():
    df = get_dataset()
    
    st.divider()

    col1, col2 = st.columns([0.80, 0.20])
    with col1:
        st.subheader("🔍 Dataset Preview")
    with col2:
        with st.expander("🗑️ Reset Session", expanded=False):
            st.warning("Are you sure? This will delete all uploaded data and clear your session.")
            if st.button("Yes, I am sure", type="primary", width="stretch"):
                reset_session()
                st.rerun()
    
    # Using .astype(str) for the first few rows to prevent Arrow serialization errors in the UI
    st.dataframe(df.head(5).astype(str), use_container_width=True)
    
    # 5. Dataset Structure
    st.subheader("📋 Dataset Structure")
    rows, cols = df.shape
    st.write(f"**Rows:** {rows}")
    st.write(f"**Columns:** {cols}")
    st.write(f"**Column Names:** {list(df.columns)}")

    # Lazy Evaluation for Profiling
    st.divider()
    st.subheader("🔍 Deep Data Profiling")
    st.write("Generating a full profile for large datasets can take time.")
    
    if st.button("Generate Data Profile", type="primary"):
        with st.spinner("Analyzing dataset..."):
            # 6. Inferred Data Types
            st.subheader("🧬 Inferred Data Types")
            st.dataframe(infer_dtypes(df), use_container_width=True)
        
            # 7. Missing Values
            st.subheader("🩹 Missing Values by Column")
            st.dataframe(missing_values(df), use_container_width=True)
        
            # 8. Duplicate Rows
            st.subheader("Duplicate Rows")
            st.write(duplicate_count(df))
        
            # 9. Numeric Summary
            st.subheader("🔢 Numeric Summary Statistics")
            n_sum = numeric_summary(df)
            if not n_sum.empty:
                st.dataframe(n_sum, use_container_width=True)
            else:
                st.info("No numeric columns available.")
                    
            # 10. Categorical Summary
            st.subheader("🔡 Categorical Summary Statistics")
            c_sum = categorical_summary(df)
            if not c_sum.empty:
                st.dataframe(c_sum, use_container_width=True)
            else:
                st.info("No categorical columns available.")
else:
    st.info("Please upload a file to begin your analysis.")

