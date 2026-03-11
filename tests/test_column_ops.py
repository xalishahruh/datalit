import pytest
import pandas as pd
from core.column_ops import (
    rename_column, drop_column, create_formula_column,
    equal_width_bins, quantile_bins
)

@pytest.fixture
def columns_df():
    return pd.DataFrame({
        "Price": [10, 20, 30, 40, 50],
        "Tax": [1, 2, 3, 4, 5]
    })

def test_rename_column(columns_df):
    renamed = rename_column(columns_df, "Price", "Cost")
    assert "Cost" in renamed.columns
    assert "Price" not in renamed.columns

def test_drop_column(columns_df):
    dropped = drop_column(columns_df, "Tax")
    assert "Tax" not in dropped.columns
    assert "Price" in dropped.columns

def test_create_formula_column(columns_df):
    new_df = create_formula_column(columns_df, "Total", "Price + Tax")
    assert "Total" in new_df.columns
    assert new_df["Total"].tolist() == [11, 22, 33, 44, 55]

def test_equal_width_bins(columns_df):
    binned = equal_width_bins(columns_df, "Price", bins=2)
    assert "Price_bin" in binned.columns
    assert len(binned["Price_bin"].unique()) <= 2

def test_quantile_bins(columns_df):
    binned = quantile_bins(columns_df, "Price", bins=2)
    assert "Price_bin" in binned.columns
    assert len(binned["Price_bin"].unique()) <= 2
