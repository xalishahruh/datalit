import pandas as pd
import numpy as np
from core import transformations, categorical_tools, numeric_tools

def test_drop_missing():
    df = pd.DataFrame({'A': [1, np.nan, 3], 'B': [4, 5, 6]})
    # Global drop
    df_clean = transformations.drop_missing_rows(df)
    assert len(df_clean) == 2
    # Column specific
    df_clean_col = transformations.drop_missing_rows(df, columns=['B'])
    assert len(df_clean_col) == 3

def test_fill_numeric():
    df = pd.DataFrame({'A': [1, np.nan, 3]})
    df_filled = transformations.fill_numeric(df, 'A', 'mean')
    assert df_filled['A'][1] == 2.0

def test_remove_duplicates():
    df = pd.DataFrame({'A': [1, 1, 2], 'B': [3, 3, 4]})
    df_unique = transformations.remove_duplicates(df)
    assert len(df_unique) == 2

def test_text_cleaning():
    df = pd.DataFrame({'name': ['  Alice ', 'BOB', 'charlie']})
    df = categorical_tools.strip_whitespace(df, 'name')
    df = categorical_tools.to_lowercase(df, 'name')
    assert df['name'][0] == 'alice'
    assert df['name'][1] == 'bob'

def test_outlier_detection():
    df = pd.DataFrame({'val': [1, 2, 3, 100]})
    outliers = numeric_tools.detect_outliers_iqr(df, 'val')
    assert len(outliers) == 1
    assert outliers['val'].iloc[0] == 100

def test_scaling():
    df = pd.DataFrame({'val': [0, 10]})
    df_scaled = numeric_tools.minmax_scale(df, ['val'])
    assert df_scaled['val'][0] == 0.0
    assert df_scaled['val'][1] == 1.0
