import pytest
import pandas as pd
import numpy as np
from core.transformations import drop_missing_rows, fill_mode
from core.numeric_tools import remove_outliers
from core.column_ops import rename_column

def test_empty_dataset():
    df = pd.DataFrame(columns=["A", "B"])
    
    # Should handle empty DataFrame gracefully without throwing exception
    cleaned_drop = drop_missing_rows(df)
    assert len(cleaned_drop) == 0
    
    renamed = rename_column(df, "A", "C")
    assert "C" in renamed.columns

def test_all_missing():
    df = pd.DataFrame({
        "A": [np.nan, np.nan],
        "B": [np.nan, np.nan]
    })
    
    cleaned_drop = drop_missing_rows(df)
    assert len(cleaned_drop) == 0

    # Ensure no exceptions are thrown when the mode is not computable
    try:
        filled = fill_mode(df, "A")
        assert len(filled) == 2
    except Exception as e:
        pytest.fail(f"fill_mode raised an exception {e} on all-nan column")

def test_single_row():
    df = pd.DataFrame({
        "A": [10],
        "B": ["Value"]
    })
    
    cleaned = remove_outliers(df, "A")
    assert len(cleaned) == 1
