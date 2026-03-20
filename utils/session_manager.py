import streamlit as st

def init_session():
    """Centralized initialization of all required session state variables."""
    keys = {
        "df": None,           # The active working dataframe
        "original_df": None,  # The pristine backup
        "history": [],        # List of dataframes for Undo (Capped at 5)
        "recipe_log": [],     # List of operations performed
        "dataset_hash": None, # Cache invalidation tracker
        "cache_keys": [],     # Cache tracking
        "uploader_key": 0,    # Key to force reset the file uploader
        "ui_state": {}        # Dictionary for transient UI state
    }
    for key, default in keys.items():
        if key not in st.session_state:
            st.session_state[key] = default

def reset_session():
    """Completely clears the session state and forces UI widgets to reset."""
    current_key = st.session_state.get("uploader_key", 0)
    st.session_state.clear()
    
    try:
        import utils.cache_manager as cache_manager
        cache_manager.clear_dataset_cache()
    except Exception:
        pass
    
    # Re-initialize to clean state immediately
    init_session()
    # Increment the uploader key to force file uploader refresh
    st.session_state["uploader_key"] = current_key + 1