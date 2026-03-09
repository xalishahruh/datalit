import pandas as pd

def get_dataset_shape(df):
    return df.shape

def get_missing_values(df):
    """Calculates and sorts missing values for better data science profiling."""
    counts = df.isna().sum()
    percents = (counts / len(df)) * 100
    
    return pd.DataFrame({
        "column": df.columns,
        "missing_values": counts.values,
        "missing_percent": percents.values
    }).sort_values("missing_values", ascending=False)

def get_duplicates(df):
    return df.duplicated().sum()

def get_summary_stats(df):
    """Generates separate summaries for numeric and categorical columns."""
    numeric_summary = df.select_dtypes(include="number").describe()
    categorical_summary = df.select_dtypes(include=["object", "category"]).describe()
    return numeric_summary, categorical_summary

def get_inferred_dtypes(df):
    """Cleaner syntax to infer and display data types."""
    return pd.DataFrame({
        "column": df.columns,
        "inferred_dtype": df.infer_objects().dtypes.values
    })