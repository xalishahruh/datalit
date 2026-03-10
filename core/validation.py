def range_check(df, column, min_val, max_val):
    return df[(df[column] < min_val) | (df[column] > max_val)]

def allowed_categories(df, column, allowed):
    return df[~df[column].isin(allowed)]

def non_null_violation(df, column):
    return df[df[column].isna()]
