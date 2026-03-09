import pandas as pd
import numpy as np

def handle_missing(df, column, strategy, fill_value=None):
    """Handles missing values based on strategy."""
    df_new = df.copy()
    if strategy == "Drop Rows":
        df_new = df_new.dropna(subset=[column])
    elif strategy == "Drop Column":
        df_new = df_new.drop(columns=[column])
    elif strategy == "Constant":
        df_new[column] = df_new[column].fillna(fill_value)
    elif strategy == "Mean":
        df_new[column] = df_new[column].fillna(df_new[column].mean())
    elif strategy == "Median":
        df_new[column] = df_new[column].fillna(df_new[column].median())
    elif strategy == "Mode":
        mode_val = df_new[column].mode()
        if not mode_val.empty:
            df_new[column] = df_new[column].fillna(mode_val[0])
    elif strategy == "Forward Fill":
        df_new[column] = df_new[column].ffill()
    elif strategy == "Backward Fill":
        df_new[column] = df_new[column].bfill()
    return df_new

def handle_duplicates(df, subset=None, keep='first'):
    """Removes duplicates."""
    return df.drop_duplicates(subset=subset, keep=keep)

def convert_types(df, column, new_type, date_format=None):
    """Converts column types."""
    df_new = df.copy()
    if new_type == "Numeric":
        # Cleaning dirty numeric values
        if df_new[column].dtype == object:
            df_new[column] = df_new[column].str.replace(r'[$,%]', '', regex=True)
        df_new[column] = pd.to_numeric(df_new[column], errors='coerce')
    elif new_type == "Categorical":
        df_new[column] = df_new[column].astype('category')
    elif new_type == "Datetime":
        if date_format:
            df_new[column] = pd.to_datetime(df_new[column], format=date_format, errors='coerce')
        else:
            df_new[column] = pd.to_datetime(df_new[column], errors='coerce')
    return df_new

def categorical_transform(df, column, transform_type, mapping=None, threshold=None):
    """Transformations for categorical columns."""
    df_new = df.copy()
    if transform_type == "Whitespace":
        df_new[column] = df_new[column].astype(str).str.strip()
    elif transform_type == "Lowercase":
        df_new[column] = df_new[column].astype(str).str.lower()
    elif transform_type == "Title Case":
        df_new[column] = df_new[column].astype(str).str.title()
    elif transform_type == "Mapping" and mapping:
        df_new[column] = df_new[column].map(mapping).fillna(df_new[column])
    elif transform_type == "Group Rare" and threshold:
        counts = df_new[column].value_counts(normalize=True)
        rare_categories = counts[counts < threshold].index
        df_new[column] = df_new[column].replace(rare_categories, 'Other')
    return df_new

def handle_outliers(df, column, method, action, threshold=1.5):
    """Detects and handles outliers."""
    df_new = df.copy()
    if not pd.api.types.is_numeric_dtype(df_new[column]):
        return df_new
    
    if method == "IQR":
        Q1 = df_new[column].quantile(0.25)
        Q3 = df_new[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
    elif method == "Z-Score":
        mean = df_new[column].mean()
        std = df_new[column].std()
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std
    else:
        return df_new

    if action == "Remove":
        df_new = df_new[(df_new[column] >= lower_bound) & (df_new[column] <= upper_bound)]
    elif action == "Cap":
        df_new[column] = df_new[column].clip(lower_bound, upper_bound)
    
    return df_new

def scale_data(df, columns, method):
    """Scales numeric columns."""
    df_new = df.copy()
    for col in columns:
        if method == "Min-Max":
            df_new[col] = (df_new[col] - df_new[col].min()) / (df_new[col].max() - df_new[col].min())
        elif method == "Standard (Z-Score)":
            df_new[col] = (df_new[col] - df_new[col].mean()) / df_new[col].std()
    return df_new

def column_operations(df, action, params):
    """Renames, removes, or creates columns."""
    df_new = df.copy()
    if action == "Rename":
        df_new = df_new.rename(columns={params['old_name']: params['new_name']})
    elif action == "Remove":
        df_new = df_new.drop(columns=params['columns'])
    elif action == "Math Formula":
        try:
            df_new[params['new_col']] = df_new.eval(params['formula'])
        except Exception as e:
            raise ValueError(f"Formula error: {e}")
    elif action == "Binning":
        if params['method'] == "Equal Width":
            df_new[params['new_col']] = pd.cut(df_new[params['col']], bins=params['bins'])
        elif params['method'] == "Quantile":
            df_new[params['new_col']] = pd.qcut(df_new[params['col']], q=params['bins'], duplicates='drop')
    return df_new
