import streamlit as st
import os

def apply_custom_styles():
    """Reads the custom CSS file and injects it into the Streamlit app."""
    css_path = os.path.join(os.getcwd(), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
