import pandas as pd

def strip_whitespace(df, column):
    df[column] = df[column].astype(str).str.strip()
    return df

def to_lowercase(df, column):
    df[column] = df[column].astype(str).str.lower()
    return df

def to_titlecase(df, column):
    df[column] = df[column].astype(str).str.title()
    return df

def map_categories(df, column, mapping):
    df[column] = df[column].map(mapping).fillna(df[column])
    return df

def group_rare_categories(df, column, threshold):
    freq = df[column].value_counts(normalize=True)
    rare = freq[freq < threshold].index
    df[column] = df[column].replace(rare, "Other")
    return df

def one_hot_encode(df, column):
    encoded = pd.get_dummies(df[column], prefix=column)
    df = pd.concat([df.drop(columns=[column]), encoded], axis=1)
    return df