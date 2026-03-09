import streamlit as st
from utils.session_manager import init_session

st.set_page_config(
    page_title="DataLit – Data Preparation Studio",
    layout="wide"
)

# Initialize session variables
init_session()

st.title("DataLit – Data Preparation Studio")

st.markdown("""
Welcome to **DataLit**.

This application allows you to:

• Upload datasets  
• Clean and transform data  
• Build visualizations  
• Export results
""")

st.info("Select a page from the sidebar to begin.")