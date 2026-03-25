def range_check(df, column, min_val, max_val):
    return df[(df[column] < min_val) | (df[column] > max_val)]

def allowed_categories(df, column, allowed):
    return df[~df[column].isin(allowed)]

def non_null_violation(df, column):
    return df[df[column].isna()]

def validate_dataset_constraints(df):
    """Checks if the dataset meets recommended constraints for full feature showcase."""
    warnings = []
    if len(df) < 1000:
        warnings.append(f"Dataset has {len(df)} rows. Recommended: ≥ 1000 rows for significant analysis.")
    if len(df.columns) < 8:
        warnings.append(f"Dataset has {len(df.columns)} columns. Recommended: ≥ 8 columns for deeper insights.")
    
    dtypes_set = set(df.dtypes.astype(str))
    has_num = any('int' in t or 'float' in t for t in dtypes_set)
    has_cat = any('object' in t or 'category' in t for t in dtypes_set)
    # has_date = any('datetime' in t for t in dtypes_set)
    if not (has_num and has_cat):
        warnings.append("Dataset lacks mixed data types (recommended: numeric + categorical).")
        
    if df.isna().sum().sum() == 0:
        warnings.append("Dataset contains no missing values. Some cleaning tools may not be demonstrable.")
        
    return warnings
