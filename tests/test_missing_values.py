import pytest
import pandas as pd
import numpy as np
from core.transformations import (
    drop_missing_rows, drop_columns_by_threshold, fill_constant,
    fill_numeric, fill_mode, fill_forward, fill_backward
)

@pytest.fixture
def df_with_missing():
    return pd.DataFrame({
        "A": [1.0, 2.0, np.nan, 4.0, 5.0],
        "B": ["cat", "dog", "cat", np.nan, "bird"],
        "C": [np.nan, np.nan, np.nan, np.nan, 5.0]
    })

def test_drop_missing_rows(df_with_missing):
    # Drop all rows with any missing value
    cleaned = drop_missing_rows(df_with_missing)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["A"] == 5.0

    # Drop missing rows considering only column A
    cleaned_col_A = drop_missing_rows(df_with_missing, ["A"])
    assert len(cleaned_col_A) == 4

def test_drop_columns_by_threshold(df_with_missing):
    # Column C has 80% missing values
    cleaned, dropped_cols = drop_columns_by_threshold(df_with_missing, threshold=0.5)
    assert "C" in dropped_cols
    assert "C" not in cleaned.columns
    assert "A" in cleaned.columns

def test_fill_constant(df_with_missing):
    cleaned = fill_constant(df_with_missing, "A", 99.0)
    assert cleaned["A"].isna().sum() == 0
    assert cleaned["A"].iloc[2] == 99.0

def test_fill_numeric(df_with_missing):
    # Mean
    cleaned_mean = fill_numeric(df_with_missing.copy(), "A", "mean")
    assert cleaned_mean["A"].isna().sum() == 0
    assert cleaned_mean["A"].iloc[2] == 3.0  # (1+2+4+5)/4 = 3.0

    # Median
    cleaned_median = fill_numeric(df_with_missing.copy(), "A", "median")
    assert cleaned_median["A"].iloc[2] == 3.0 # median of 1, 2, 4, 5 is 3.0

def test_fill_mode(df_with_missing):
    cleaned = fill_mode(df_with_missing, "B")
    assert cleaned["B"].iloc[3] == "cat" # mode is cat

def test_fill_forward(df_with_missing):
    cleaned = fill_forward(df_with_missing, "A")
    assert cleaned["A"].iloc[2] == 2.0 # Forward filled from index 1

def test_fill_backward(df_with_missing):
    cleaned = fill_backward(df_with_missing, "A")
    assert cleaned["A"].iloc[2] == 4.0 # Backward filled from index 3
