import streamlit as st
import pandas as pd

def init_state():
    """Initializes the session state variables if they don't exist."""
    if 'original_df' not in st.session_state:
        st.session_state.original_df = None
    if 'working_df' not in st.session_state:
        st.session_state.working_df = None
    if 'recipe_log' not in st.session_state:
        st.session_state.recipe_log = []
    if 'history' not in st.session_state:
        st.session_state.history = []

def set_dataset(df):
    """Sets the initial dataset and resets the working copy and log."""
    st.session_state.original_df = df
    st.session_state.working_df = df.copy()
    st.session_state.recipe_log = []
    st.session_state.history = [df.copy()]

def add_transformation(op_name, params, affected_cols, df_after):
    """Logs a transformation and updates the working dataset."""
    import datetime
    log_entry = {
        'operation': op_name,
        'parameters': params,
        'affected_columns': affected_cols,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.recipe_log.append(log_entry)
    st.session_state.history.append(df_after.copy())
    st.session_state.working_df = df_after

def undo_last_transformation():
    """Removes the last step from the log and restores the previous dataframe state."""
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()
        st.session_state.recipe_log.pop()
        st.session_state.working_df = st.session_state.history[-1].copy()
        return True
    return False

def reset_to_original():
    """Resets the working dataframe to the original upload."""
    if st.session_state.original_df is not None:
        st.session_state.working_df = st.session_state.original_df.copy()
        st.session_state.recipe_log = []
        st.session_state.history = [st.session_state.original_df.copy()]
        return True
    return False
