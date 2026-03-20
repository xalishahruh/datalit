import streamlit as st
import pandas as pd
import datetime
import utils.data_helpers as data_helpers
import utils.cache_manager as cache_manager
from utils.session_manager import init_session as _init_session, reset_session as _reset_session
from utils.cache_manager import clear_dataset_cache
from utils.data_helpers import generate_dataset_hash

# Constants
MAX_HISTORY_STATES = 5

def init_manager():
    """Initializes all required session state variables once, delegating to central session manager."""
    _init_session()

def update_dataset_hash(df):
    """Calculates dataset signature and forces cache clear."""
    new_hash = generate_dataset_hash(df)
    st.session_state["dataset_hash"] = new_hash
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
    
    # Calculate dataset hash and clear global cache for the new dataset
    st.session_state["dataset_hash"] = data_helpers.generate_dataset_hash(df)
    cache_manager.clear_dataset_cache()
    
    update_dataset_hash(df)

def get_dataset():
    """Returns the current working dataframe."""
    return st.session_state.get("df")

def dataset_exists():
    """True if a dataset has been uploaded."""
    return st.session_state.get("df") is not None

def add_transformation(op_name, params, affected_cols, df_after):
    """Logs a change, updates the undo history, caps memory, and clears cache."""
    log_entry = {
        'operation': op_name,
        'parameters': params,
        'affected_columns': affected_cols,
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state["recipe_log"].append(log_entry)
    
    # Capitalize on memory by preventing infinite copy scaling
    st.session_state["history"].append(df_after.copy())
    st.session_state["df"] = df_after
    
    st.session_state["dataset_hash"] = data_helpers.generate_dataset_hash(df_after)
    if len(st.session_state["history"]) > MAX_HISTORY_STATES:
        st.session_state["history"] = st.session_state["history"][-MAX_HISTORY_STATES:]
        
    clear_dataset_cache()


def undo_transformation():
    """Goes back one step in time safely."""
    if len(st.session_state["history"]) > 1:
        st.session_state["history"].pop()
        
        # We can also pop the recipe log, but if history was capped, recipe log might be longer.
        # Safe pop for recipe_log
        if len(st.session_state["recipe_log"]) > 0:
            st.session_state["recipe_log"].pop()
            
        st.session_state["df"] = st.session_state["history"][-1].copy()
        st.session_state["dataset_hash"] = data_helpers.generate_dataset_hash(st.session_state["df"])
        clear_dataset_cache() # Invalidate cache after undo
        return True
    return False

def reset_dataset():
    """Wipes all changes and returns to the original file."""
    if st.session_state["original_df"] is not None:
        st.session_state["df"] = st.session_state["original_df"].copy()
        st.session_state["history"] = [st.session_state["original_df"].copy()]
        st.session_state["recipe_log"] = []
        st.session_state["dataset_hash"] = data_helpers.generate_dataset_hash(st.session_state["df"])
        cache_manager.clear_dataset_cache()
        return True
    return False

def reset_session():
    """Delegates to the central session annihilator."""
    _reset_session()
    clear_dataset_cache()

def update_dataset(df):
    st.session_state["df"] = df
    st.session_state["dataset_hash"] = data_helpers.generate_dataset_hash(df)
    update_dataset_hash(df)
