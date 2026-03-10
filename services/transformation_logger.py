import streamlit as st
from datetime import datetime

def log_transformation(operation, parameters):

    entry = {
        "operation": operation,
        "parameters": parameters,
        "timestamp": str(datetime.now())
    }

    if "pipeline" not in st.session_state:
        st.session_state["pipeline"] = []

    st.session_state["pipeline"].append(entry)