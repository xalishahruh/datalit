import pandas as pd
import streamlit as st
import json

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

@st.cache_data
def load_json(file):
    # Try reading as orient='records' first, typical for many JSON datasets
    try:
        return pd.read_json(file)
    except:
        # Fallback for other formats
        data = json.load(file)
        return pd.json_normalize(data)

@st.cache_data
def load_google_sheet(sheet_url_or_id):
    """
    Skeleton for Google Sheets loading. 
    Ideally uses gspread or pandas read_csv for public sheets.
    """
    try:
        if "docs.google.com/spreadsheets" in sheet_url_or_id:
            # Simple approach for public sheets: convert to CSV export URL
            sheet_id = sheet_url_or_id.split("/d/")[1].split("/")[0]
            url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            return pd.read_csv(url)
        else:
            return None
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
        return None
