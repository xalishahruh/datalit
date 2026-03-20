import streamlit as st
import pandas as pd

def clear_dataset_cache():
    """
    Clears all st.cache_data and st.cache_resource decorated functions globally.
    This must be called whenever the underlying dataset changes drastically or is reset.
    """
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
    except Exception:
        pass

@st.cache_data(show_spinner=False)
def get_cached_profile_stats(df: pd.DataFrame, dataset_hash: str) -> dict:
    """
    Computes expensive profiling metrics. 
    It explicitly uses dataset_hash to ensure cache invalidation happens 
    whenever the hash fundamentally changes.
    """
    if df is None or df.empty:
        return {}
    
    stats = {}
    stats['num_rows'] = df.shape[0]
    stats['num_cols'] = df.shape[1]
    stats['memory_usage'] = df.memory_usage(deep=True).sum()
    stats['missing_cells'] = df.isnull().sum().sum()
    stats['duplicate_rows'] = df.duplicated().sum()
    
    return stats
