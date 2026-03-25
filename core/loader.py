import pandas as pd
import os
import streamlit as st

def _load_csv(file):
    """Internal helper to load CSV with encoding fallback."""
    try:
        return pd.read_csv(file, on_bad_lines="skip", encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, on_bad_lines="skip", encoding="ISO-8859-1", low_memory=False)

def _load_gsheets(url):
    """Internal helper to load Google Sheets from a public export URL."""
    try:
        # Convert sharing URL to export URL if needed
        if "/edit" in url:
            url = url.replace("/edit", "/export?format=csv")
        elif "docs.google.com" in url and "export" not in url:
            url = url + "/export?format=csv"
        
        return pd.read_csv(url)
    except Exception as e:
        raise Exception(f"Failed to load Google Sheet. Ensure the link is public: {str(e)}")

@st.cache_data
def load_dataset(file, file_type):
    """
    Intelligently loads a dataset based on the provided file_type.
    """
    if file_type == "gsheets":
        return _load_gsheets(file)

    # Normalize file_type
    ext = f".{file_type.lower()}" if not file_type.startswith(".") else file_type.lower()
    
    # Mapping of extensions to loading functions
    loaders = {
        ".csv": _load_csv,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".json": pd.read_json
    }

    loader_func = loaders.get(ext)
    
    if not loader_func:
        raise ValueError(f"The format '{file_type}' is not supported. Please use CSV, Excel, JSON, or Google Sheets.")

    try:
        return loader_func(file)
    except Exception as e:
        raise Exception(f"Error processing the {file_type} file: {str(e)}")



