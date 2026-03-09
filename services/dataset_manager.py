import streamlit as st
import pandas as pd
import datetime

def init_manager():
    """Initializes all required session state variables once."""
    keys = {
        "df": None,           # The active working dataframe
        "original_df": None,  # The pristine backup
        "history": [],        # List of dataframes for Undo
        "recipe_log": []      # List of operations performed
    }
    for key, default in keys.items():
        if key not in st.session_state:
            st.session_state[key] = default

def save_dataset(df, name="Initial Upload"):
    """
    Sets a new dataset and resets the history/logs.
    Used during initial file upload.
    """
    st.session_state["original_df"] = df.copy()
    st.session_state["df"] = df.copy()
    st.session_state["history"] = [df.copy()]
    st.session_state["recipe_log"] = []

def get_dataset():
    """Returns the current working dataframe."""
    return st.session_state.get("df")

def dataset_exists():
    """True if a dataset has been uploaded."""
    return st.session_state.get("df") is not None

def add_transformation(op_name, params, affected_cols, df_after):
    """Logs a change and updates the undo history."""
    log_entry = {
        'operation': op_name,
        'parameters': params,
        'affected_columns': affected_cols,
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state["recipe_log"].append(log_entry)
    st.session_state["history"].append(df_after.copy())
    st.session_state["df"] = df_after

def undo_transformation():
    """Goes back one step in time."""
    if len(st.session_state["history"]) > 1:
        st.session_state["history"].pop()
        st.session_state["recipe_log"].pop()
        st.session_state["df"] = st.session_state["history"][-1].copy()
        return True
    return False

def reset_dataset():
    """Wipes all changes and returns to the original file."""
    if st.session_state["original_df"] is not None:
        save_dataset(st.session_state["original_df"])
        return True
    return False
