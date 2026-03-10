import pandas as pd

# Missing Values
def drop_missing_rows(df, columns=None):
    if columns:
        return df.dropna(subset=columns)
    return df.dropna()

def drop_columns_by_threshold(df, threshold):
    missing_ratio = df.isna().mean()
    cols = missing_ratio[missing_ratio > threshold].index
    return df.drop(columns=cols), list(cols)

def fill_constant(df, column, value):
    df[column] = df[column].fillna(value)
    return df

def fill_numeric(df, column, method):
        numeric_series = pd.to_numeric(df[column], errors="coerce")
        if method == "mean":
            val = numeric_series.mean()
        elif method == "median":
            val = numeric_series.median()
        else:
            raise ValueError("Method must be mean or median")
        df[column] = numeric_series.fillna(val)
        return df

def fill_mode(df, column):
    mode_value = df[column].mode()
    if len(mode_value) == 0:
        return df
    df[column] = df[column].fillna(mode_value[0])
    return df


def fill_forward(df, column):
    df[column] = df[column].fillna(method="ffill")
    return df

def fill_backward(df, column):
    df[column] = df[column].fillna(method="bfill")
    return df

# Duplicates
def detect_duplicates(df):
    return df[df.duplicated(keep=False)]

def detect_duplicates_subset(df, columns):
    return df[df.duplicated(subset=columns, keep=False)]

def remove_duplicates(df, subset=None, keep="first"):
    return df.drop_duplicates(subset=subset, keep=keep)

# Data Types
def clean_numeric_strings(df, column):
    df[column] = (
        df[column]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
    )
    return df

def convert_to_numeric(df, column):
    df[column] = pd.to_numeric(df[column], errors="coerce")
    return df

def convert_to_datetime(df, column, fmt=None):
    if fmt and fmt.strip() != "":
        df[column] = pd.to_datetime(
            df[column],
            format=fmt,
            errors="coerce"
        )
    else:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
            infer_datetime_format=True
        )
    return df


def convert_to_category(df, column):
    df[column] = df[column].astype("category")
    return df