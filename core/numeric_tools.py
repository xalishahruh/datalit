import pandas as pd
import numpy as np

# Outliers
def detect_outliers_iqr(df, column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df[(df[column] < lower) | (df[column] > upper)]

def detect_outliers_zscore(df, column, threshold=3):
    """Detect outliers using Z-score method."""
    z_scores = (df[column] - df[column].mean()) / df[column].std()
    return df[np.abs(z_scores) > threshold]

def cap_outliers(df, column):
    lower = df[column].quantile(0.01)
    upper = df[column].quantile(0.99)
    df[column] = df[column].clip(lower, upper)
    return df

def remove_outliers(df, column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df[(df[column] >= lower) & (df[column] <= upper)]

# Scaling (Manual implementations to remove sklearn dependency)
def minmax_scale(df, columns):
    for col in columns:
        min_val = df[col].min()
        max_val = df[col].max()
        if max_val != min_val:
            df[col] = (df[col] - min_val) / (max_val - min_val)
        else:
            df[col] = 0.0
    return df

def zscore_scale(df, columns):
    for col in columns:
        mean_val = df[col].mean()
        std_val = df[col].std()
        if std_val != 0:
            df[col] = (df[col] - mean_val) / std_val
        else:
            df[col] = 0.0
    return df