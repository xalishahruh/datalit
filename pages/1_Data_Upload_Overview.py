import streamlit as st
import pandas as pd
from core.loader import load_csv, load_excel, load_json, load_google_sheet
from core.state_manager import set_dataset, reset_to_original
from core.profiling import get_basic_info, get_column_stats, get_numeric_summary
from utils.ui_utils import apply_custom_styles

st.set_page_config(page_title="Upload & Overview", layout="wide")
apply_custom_styles()

st.title("📂 Data Upload & Overview")

# Sidebar - Reset Button
with st.sidebar:
    if st.button("🔄 Reset Session", use_container_width=True):
        if reset_to_original():
            st.success("Session reset to original state.")
            st.rerun()

# Upload Section
upload_tab, gsheet_tab = st.tabs(["📁 File Upload", "🌐 Google Sheets"])

with upload_tab:
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"])
    if uploaded_file:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        df = None
        if file_ext == "csv":
            df = load_csv(uploaded_file)
        elif file_ext == "xlsx":
            df = load_excel(uploaded_file)
        elif file_ext == "json":
            df = load_json(uploaded_file)
        
        if df is not None:
            if st.button("🚀 Load Dataset"):
                set_dataset(df)
                st.success("Dataset loaded successfully!")

with gsheet_tab:
    sheet_url = st.text_input("Paste Google Sheet URL (Public)")
    if sheet_url:
        if st.button("🔗 Load from GSheets"):
            df = load_google_sheet(sheet_url)
            if df is not None:
                set_dataset(df)
                st.success("GSheet loaded successfully!")

# Overview Section
if st.session_state.working_df is not None:
    working_df = st.session_state.working_df
    
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    info = get_basic_info(working_df)
    
    col1.metric("Rows", info["rows"])
    col2.metric("Columns", info["cols"])
    col3.metric("Duplicate Rows", info["duplicates"])
    col4.metric("Missing Values (%)", f"{ (working_df.isnull().sum().sum() / working_df.size) * 100:.2f}%")

    st.subheader("📊 Data Statistics")
    col_stats = get_column_stats(working_df)
    st.dataframe(col_stats, use_container_width=True)

    st.subheader("🔢 Numeric Summary")
    num_summary = get_numeric_summary(working_df)
    if not num_summary.empty:
        st.dataframe(num_summary, use_container_width=True)
    else:
        st.info("No numeric columns found for summary statistics.")

    st.subheader("👀 Data Preview (First 10 rows)")
    st.dataframe(working_df.head(10), use_container_width=True)

else:
    st.info("Please upload a dataset to see the overview.")
