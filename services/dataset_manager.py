import streamlit as st
import pandas as pd
import datetime
import time
from utils.session_manager import init_session as _init_session, reset_session as _reset_session
from utils.cache_manager import clear_dataset_cache
from utils.data_helpers import generate_dataset_hash

# Constants
MAX_HISTORY_STATES = 5

def init_manager():
    """Initializes all required session state variables once, delegating to central session manager."""
    _init_session()

def _update_state(df):
    """Internal helper to sync hash and clear cache when data changes."""
    st.session_state["dataset_hash"] = generate_dataset_hash(df)
    clear_dataset_cache()

def store_dataset(df, name="Initial Upload"):
    """
    Sets a new dataset and resets the history/logs.
    Used during initial file upload.
    """
    st.session_state["original_df"] = df.copy()
    st.session_state["df"] = df.copy()
    st.session_state["history"] = [df.copy()]
    st.session_state["recipe_log"] = []
    
    _update_state(df)

def get_dataset():
    """Returns the current working dataframe."""
    return st.session_state.get("df")

def dataset_exists():
    """True if a dataset has been uploaded."""
    return st.session_state.get("df") is not None

def add_transformation(op_name, params, affected_cols, df_after, duration=None):
    """Logs a change, updates the undo history, caps memory, and clears cache."""
    log_entry = {
        'operation': op_name,
        'parameters': params,
        'affected_columns': affected_cols,
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S"),
        'duration': f"{duration:.4f}s" if duration is not None else "N/A"
    }
    st.session_state["recipe_log"].append(log_entry)
    
    # Capitalize on memory by preventing infinite copy scaling
    st.session_state["history"].append(df_after.copy())
    if len(st.session_state["history"]) > MAX_HISTORY_STATES:
        st.session_state["history"] = st.session_state["history"][-MAX_HISTORY_STATES:]
        
    st.session_state["df"] = df_after
    _update_state(df_after)

def undo_transformation():
    """Goes back one step in time safely."""
    if len(st.session_state["history"]) > 1:
        st.session_state["history"].pop()
        
        # If history was capped, log might have more steps than history array length.
        # But we pop latest available.
        if len(st.session_state["recipe_log"]) > 0:
            st.session_state["recipe_log"].pop()
            
        st.session_state["df"] = st.session_state["history"][-1].copy()
        _update_state(st.session_state["df"])
        return True
    return False

def reset_dataset():
    """Wipes all changes and returns to the original file."""
    if st.session_state["original_df"] is not None:
        st.session_state["df"] = st.session_state["original_df"].copy()
        st.session_state["history"] = [st.session_state["original_df"].copy()]
        st.session_state["recipe_log"] = []
        _update_state(st.session_state["df"])
        return True
    return False

def reset_session():
    """Delegates to the central session annihilator."""
    _reset_session()
    clear_dataset_cache()

def update_dataset(df):
    """Updates the work area directly (use sparingly outside transformations)."""
    st.session_state["df"] = df
    _update_state(df)
