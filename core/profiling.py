import pandas as pd
import streamlit as st

@st.cache_data
def infer_dtypes(df):
    """Profiling: Returns inferred data types for each column."""
    return pd.DataFrame({
        "column": df.columns,
        "inferred_dtype": df.infer_objects().dtypes.values
    })

@st.cache_data
def missing_values(df):
    """Profiling: Calculates and sorts missing values count and percentage."""
    counts = df.isna().sum()
    percents = (counts / len(df)) * 100
    
    return pd.DataFrame({
        "column": df.columns,
        "missing_values": counts.values,
        "missing_percent": percents.values
    }).sort_values("missing_values", ascending=False)

@st.cache_data
def duplicate_count(df):
    """Profiling: Returns the total count of duplicate rows."""
    return df.duplicated().sum()

@st.cache_data
def numeric_summary(df):
    """Profiling: Returns descriptive statistics for numeric columns (+ Skewness/Kurtosis)."""
    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return pd.DataFrame()
        
    desc = num_df.describe()
    desc.loc["skewness"] = num_df.skew()
    desc.loc["kurtosis"] = num_df.kurtosis()
    return desc

@st.cache_data
def categorical_summary(df):
    """Profiling: Returns descriptive statistics for categorical columns (+ Cardinality)."""
    cat_df = df.select_dtypes(include=["object", "category"])
    if cat_df.empty:
        return pd.DataFrame()
        
    desc = cat_df.describe()
    cardinality = (desc.loc["unique"] / len(cat_df) * 100).round(2).astype(str) + "%"
    desc.loc["cardinality (%)"] = cardinality
    return desc

@st.cache_data
def memory_optimization_potential(df):
    """Calculates current memory and potential savings through downcasting."""
    current_mem = df.memory_usage(deep=True).sum() / (1024 * 1024) # MB
    
    optimized_mem = current_mem
    savings = 0
    for col in df.columns:
        col_mem = df[col].memory_usage(deep=True) / (1024 * 1024)
        if 'float' in str(df[col].dtype) or 'int' in str(df[col].dtype):
            savings += col_mem * 0.5
        elif df[col].dtype == 'object':
            if df[col].nunique() / len(df) < 0.5:
                savings += col_mem * 0.7
                
    return {
        "current_mb": round(current_mem, 2),
        "optimized_mb": round(current_mem - savings, 2),
        "savings_pct": round((savings / current_mem) * 100, 1) if current_mem > 0 else 0
    }
