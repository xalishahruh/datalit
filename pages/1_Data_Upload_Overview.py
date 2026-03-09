import streamlit as st
from core.loader import load_dataset
from core.profiling import (
    get_inferred_dtypes,
    get_missing_values,
    get_duplicates,
    get_summary_stats
)
from services.dataset_manager import (
    save_dataset,
    get_dataset,
    dataset_exists,
    init_manager
)

# 1. Initialize state
init_manager()

st.title("📂 Data Upload & Overview")

# 2. Upload Section
uploaded_file = st.file_uploader(
    "Upload your dataset (CSV, Excel, or JSON)",
    type=["csv", "xlsx", "json"]
)

if uploaded_file is not None:
    try:
        # Load and store only if new file
        df = load_dataset(uploaded_file)
        save_dataset(df)
        st.success(f"Successfully loaded '{uploaded_file.name}'")
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")

# 3. Overview Section (Visible only if data is loaded)
if dataset_exists():
    df = get_dataset()
    
    st.divider()
    
    # 3.1 Dataset Preview
    st.subheader("🔍 Dataset Preview")
    # Using .astype(str) for the first few rows to prevent Arrow serialization errors in the UI
    st.dataframe(df.head(10).astype(str), use_container_width=True)
    
    # 3.2 Structure
    rows, cols = df.shape
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Rows", rows)
    with col2:
        st.metric("Total Columns", cols)

    # 3.3 Data Profiles
    tab1, tab2, tab3 = st.tabs(["🧬 Data Types", "🩹 Missing Values", "📊 Stats Summary"])
    
    with tab1:
        st.subheader("Inferred Data Types")
        st.dataframe(get_inferred_dtypes(df), use_container_width=True)

    with tab2:
        st.subheader("Missing Values Analysis")
        st.dataframe(get_missing_values(df), use_container_width=True)
        st.write(f"**Duplicate Rows Found:** {get_duplicates(df)}")

    with tab3:
        num_sum, cat_sum = get_summary_stats(df)
        
        st.subheader("Numeric Summary")
        if not num_sum.empty:
            st.dataframe(num_sum, use_container_width=True)
        else:
            st.info("No numeric columns available.")
            
        st.subheader("Categorical Summary")
        if not cat_sum.empty:
            st.dataframe(cat_sum, use_container_width=True)
        else:
            st.info("No categorical columns available.")
else:
    st.info("Please upload a file to begin your analysis.")
