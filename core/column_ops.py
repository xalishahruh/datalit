import pandas as pd
import numpy as np

def rename_column(df, old_name, new_name):
    return df.rename(columns={old_name: new_name})

def drop_column(df, column):
    return df.drop(columns=[column])

def create_formula_column(df, new_column, formula):
    df[new_column] = eval(formula, {}, df)
    return df

def equal_width_bins(df, column, bins):
    df[column + "_bin"] = pd.cut(df[column], bins)
    return df

def quantile_bins(df, column, bins):
    df[column + "_bin"] = pd.qcut(df[column], bins)
    return df