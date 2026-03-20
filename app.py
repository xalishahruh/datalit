import streamlit as st
from utils.session_manager import init_session
from utils.ui_utils import apply_custom_styles
from services.dataset_manager import init_manager

# Page Configuration
st.set_page_config(
    page_title="DataLit – Data Preparation Studio",
    layout="wide"
)

# Initialize session variables
init_manager()
apply_custom_styles()

# Hero Section
st.markdown("""
    <div style="background-color: #6C5CE7; padding: 60px; border-radius: 20px; color: white; margin-bottom: 40px; text-align: center;">
        <h1 style="color: white; font-size: 3.5rem; margin-bottom: 10px;">DataLit 💎</h1>
        <p style="font-size: 1.4rem; opacity: 0.9;">Professional Data Transformation & AI-Assisted Cleaning Studio</p>
    </div>
""", unsafe_allow_html=True)

# Main Features Layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📂 Load & Profile")
    st.write("Upload your data and get instant insights into missing values, duplicates, and statistical distribution.")

with col2:
    st.markdown("### 🤖 AI Assistant")
    st.write("Let our rule-based engine and optional LLM insights guide you through the cleaning process.")

with col3:
    st.markdown("### 📊 Visualize & Export")
    st.write("Create stunning visualizations and export your clean, ready-to-use dataset with a full recipe log.")

st.divider()

# Call to Action
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.info("👈 Select **Overview** from the sidebar to upload your first dataset and begin your journey.")