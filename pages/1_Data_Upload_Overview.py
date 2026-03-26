import streamlit as st
import pandas as pd
from utils.ui_utils import apply_custom_styles
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
from core.validation import validate_dataset_constraints

# Page Config
st.set_page_config(page_title="DataLit | Data Overview", page_icon="📂", layout="wide")
apply_custom_styles()
init_manager()

# Header
st.title("📂 Data Upload & Profile")
st.caption("Upload your raw dataset to explore its structure, statistics, and quality.")
st.divider()

# Upload Section
up_tab1, up_tab2, up_tab3 = st.tabs(["📁 File Upload", "🌐 Google Sheets", "🎁 Sample Datasets"])

with up_tab1:
    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Upload your dataset (CSV, Excel, or JSON)",
            type=["csv", "xlsx", "json"],
            key=f"uploader_{st.session_state.get('uploader_key', 0)}"
        )
    with col_up2:
        if dataset_exists():
            with st.expander("🗑️ Reset Session", expanded=False):
                st.warning("All uploaded data and transformations will be cleared.")
                if st.button("Reset Everything", type="primary", use_container_width=True):
                    reset_session()
                    st.rerun()

with up_tab2:
    gs_url = st.text_input("Paste Google Sheets Share Link:", placeholder="https://docs.google.com/spreadsheets/d/...")
    st.caption("Ensure the sheet is set to 'Anyone with the link can view'.")
    load_gs = st.button("Connect & Load Sheet", type="primary")

with up_tab3:
    st.markdown("Load a built-in dataset to explore DataLit's capabilities without needing your own files.")
    sample_choice = st.selectbox("Select a Sample Dataset:", ["Titanic Insights", "Penguins Ecosystem", "Diamonds Premium (50k+ rows)", "Insurance Analytics (1.3k rows)"])
    
    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        load_sample = st.button("Load Sample", type="primary", help="Instantly load this standardized sample dataset into the app for exploration and cleaning.")
    with col_info:
        st.info("💡 **Tip:** Use these datasets to test missing value imputation, rule-based column operations, and AI visualizations.")

if uploaded_file is not None:
    try:
        if not dataset_exists() or st.session_state.get("last_uploaded") != uploaded_file.name:
            with st.spinner(f"Loading '{uploaded_file.name}'..."):
                file_type = uploaded_file.name.split(".")[-1]
                df = load_dataset(uploaded_file, file_type)
                store_dataset(df)
                st.session_state["last_uploaded"] = uploaded_file.name
                st.success(f"Successfully loaded '{uploaded_file.name}'")
                st.rerun()
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")

if load_gs and gs_url:
    try:
        with st.spinner("Connecting to Google Sheets..."):
            df = load_dataset(gs_url, "gsheets")
            store_dataset(df)
            st.session_state["last_uploaded"] = "Google Sheet"
            st.success("Successfully loaded Google Sheet!")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to load Google Sheet: {e}")

if up_tab3 and locals().get('load_sample'):
    try:
        with st.spinner("Loading sample dataset..."):
            if sample_choice == "Titanic Insights":
                df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
            elif sample_choice == "Penguins Ecosystem":
                df = pd.read_csv("https://raw.githubusercontent.com/allisonhorst/palmerpenguins/master/inst/extdata/penguins.csv")
            elif sample_choice == "Diamonds Premium (50k+ rows)":
                df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv")
            elif sample_choice == "Insurance Analytics (1.3k rows)":
                df = pd.read_csv("https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv")
            
            store_dataset(df)
            st.session_state["last_uploaded"] = f"Sample: {sample_choice}"
            st.success(f"Successfully loaded '{sample_choice}'!")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to load sample dataset: {e}")

# Overview Section
if dataset_exists():
    df = get_dataset()
    
    # Dataset Constraints Warnings
    warnings = validate_dataset_constraints(df)
    if warnings:
        with st.expander("⚠️ Dataset Structural Warnings (Checklist Constraints)", expanded=False):
            for w in warnings:
                st.warning(w)
    
    # Quick Metrics
    st.subheader("🔍 Dataset Overview")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Rows", f"{len(df):,}")
    with m2:
        st.metric("Total Columns", f"{len(df.columns)}")
    with m3:
        st.metric("Duplicate Rows", f"{df.duplicated().sum()}")
    with m4:
        st.metric("Missing Cells", f"{df.isna().sum().sum()}")

    # Preview
    with st.expander("👀 View Dataset Preview (First 5 Rows)", expanded=True):
        st.dataframe(df.head(5).astype(str), use_container_width=True)
    
    # Profiling Button
    st.divider()
    st.subheader("🧬 Statistical Profiling")
    
    if "profile_visible" not in st.session_state:
        st.session_state.profile_visible = False
        
    import time
    
    if not st.session_state.profile_visible:
        if st.button("Generate Detailed Profile", type="primary", use_container_width=True):
            with st.status("🔍 Initiating Deep Data Scan...", expanded=True) as status:
                st.write("Analysing memory optimization vectors...")
                time.sleep(0.7)
                st.write("Computing distribution skewness & kurtosis...")
                time.sleep(0.7)
                st.write("Cross-referencing categorical cardinalities...")
                time.sleep(0.7)
                status.update(label="Profiling Complete!", state="complete", expanded=False)
            
            st.session_state.profile_visible = True
            st.rerun()
            
    if st.session_state.profile_visible:
        p_tab1, p_tab2, p_tab3, p_tab4 = st.tabs(["📦 Dtypes & Missing", "🔢 Numeric Stats", "🔡 Categorical Stats", "⚡ Memory Optimization (Niche)"])
        
        with p_tab1:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown("#### Inferred Data Types")
                st.dataframe(infer_dtypes(df), use_container_width=True)
            with col_p2:
                st.markdown("#### Missing Values Distribution")
                st.dataframe(missing_values(df), use_container_width=True)
        
        with p_tab2:
            st.markdown("#### Descriptive Statistics (Numeric + Profound)")
            st.caption("Now includes distribution skewness & kurtosis to identify non-normal feature behaviors before modeling.")
            n_sum = numeric_summary(df)
            if not n_sum.empty:
                st.dataframe(n_sum, use_container_width=True)
            else:
                st.info("No numeric columns found.")
        
        with p_tab3:
            st.markdown("#### Categorical Overview (+ Cardinality)")
            st.caption("Now includes cardinality percentages to flag features that might require heavy one-hot encoding or grouping.")
            c_sum = categorical_summary(df)
            if not c_sum.empty:
                st.dataframe(c_sum, use_container_width=True)
            else:
                st.info("No categorical columns found.")
                
        with p_tab4:
            from core.profiling import memory_optimization_potential
            mem_data = memory_optimization_potential(df)
            
            st.markdown("#### Database Footprint & Compression Potential")
            st.markdown("This profound metric analyzes column-level cardinality and floating-point precision to calculate hypothetical data compression—vital for large-scale data engineering environments.")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Current RAM Usage", f"{mem_data['current_mb']} MB")
            c2.metric("Optimized Potential", f"{mem_data['optimized_mb']} MB", delta=f"-{mem_data['savings_pct']}%", delta_color="inverse")
            c3.metric("Data Density Score", f"{100 - mem_data['savings_pct']}/100", help="Higher means your data is already highly memory-efficient.")
            
        st.write("")
        st.write("")
        col_reg1, col_reg2, col_reg3 = st.columns([1, 2, 1])
        with col_reg2:
            if st.button("🔄 Regenerate Detailed Profile", use_container_width=True):
                st.session_state.profile_visible = False
                st.rerun()

else:
    st.markdown("""
        <div style="text-align: center; color: #95a5a6; padding: 50px;">
            <p style="font-size: 1.5rem;">No data found. Upload a file above to begin.</p>
        </div>
    """, unsafe_allow_html=True)

