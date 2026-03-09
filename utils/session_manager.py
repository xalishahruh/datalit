# Placeholder for utils/session_manager.py
import streamlit as st

def init_session():

    if "df" not in st.session_state:
        st.session_state["df"] = None

    if "pipeline" not in st.session_state:
        st.session_state["pipeline"] = []

    if "logs" not in st.session_state:
        st.session_state["logs"] = []