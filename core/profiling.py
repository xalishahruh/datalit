import pandas as pd

def infer_dtypes(df):
    """Profiling: Returns inferred data types for each column."""
    return pd.DataFrame({
        "column": df.columns,
        "inferred_dtype": df.infer_objects().dtypes.values
    })

def missing_values(df):
    """Profiling: Calculates and sorts missing values count and percentage."""
    counts = df.isna().sum()
    percents = (counts / len(df)) * 100
    
    return pd.DataFrame({
        "column": df.columns,
        "missing_values": counts.values,
        "missing_percent": percents.values
    }).sort_values("missing_values", ascending=False)

def duplicate_count(df):
    """Profiling: Returns the total count of duplicate rows."""
    return df.duplicated().sum()

def numeric_summary(df):
    """Profiling: Returns descriptive statistics for numeric columns."""
    return df.select_dtypes(include="number").describe()

def categorical_summary(df):
    """Profiling: Returns descriptive statistics for categorical columns."""
    return df.select_dtypes(include=["object", "category"]).describe()
