import pandas as pd

def get_dataset_shape(df):
    return df.shape

def get_missing_values(df):
    missing_count = df.isna().sum()
    missing_percent = (missing_count / len(df)) * 100

    return (
        pd.DataFrame({
            "column": df.columns,
            "missing_values": missing_count.values,
            "missing_percent": missing_percent.values
        })
        .sort_values("missing_values", ascending=False)
    )

def get_duplicates(df):
    return df.duplicated().sum()

def get_summary_stats(df):

    numeric_summary = df.select_dtypes(include="number").describe()

    categorical_summary = (
        df.select_dtypes(include=["object", "category"])
        .describe()
    )

    return numeric_summary, categorical_summary

def get_inferred_dtypes(df):
    inferred = df.infer_objects().dtypes
    return inferred.reset_index().rename(
        columns={"index": "column", 0: "inferred_dtype"}
    )