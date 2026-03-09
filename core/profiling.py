import pandas as pd

def get_basic_info(df):
    """Returns basic stats about the dataframe."""
    return {
        "rows": df.shape[0],
        "cols": df.shape[1],
        "duplicates": df.duplicated().sum()
    }

def get_column_stats(df):
    """Returns a stats dataframe with types and missingness."""
    stats = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes.values.astype(str),
        'Missing Values': df.isnull().sum().values,
        'Missing %': (df.isnull().sum().values / len(df)) * 100
    })
    return stats

def get_numeric_summary(df):
    """Returns describe() for numeric columns."""
    return df.describe()
