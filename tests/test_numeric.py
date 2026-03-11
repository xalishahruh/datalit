import pytest
import pandas as pd
import numpy as np
from core.numeric_tools import (
    detect_outliers_iqr, cap_outliers, remove_outliers,
    minmax_scale, zscore_scale
)

@pytest.fixture
def numeric_df():
    # 1, 2, 3, 4, 5, 6, 7 are normal. 100 is an outlier.
    return pd.DataFrame({
        "Values": [1, 2, 3, 4, 5, 2, 1, 100],
        "Scores": [10, 20, 30, 40, 50, 60, 70, 80]
    })

def test_detect_outliers_iqr(numeric_df):
    outliers = detect_outliers_iqr(numeric_df, "Values", threshold=1.5)
    assert len(outliers) == 1
    assert outliers.iloc[0]["Values"] == 100

def test_remove_outliers(numeric_df):
    cleaned = remove_outliers(numeric_df, "Values", threshold=1.5)
    assert len(cleaned) == 7
    assert 100 not in cleaned["Values"].tolist()

def test_cap_outliers(numeric_df):
    # Instead of capping at percentiles directly without IQR, the cap_outliers function caps at percentiles
    cleaned = cap_outliers(numeric_df, "Values", lower_percentile=0.05, upper_percentile=0.95)
    # The max value should be capped
    assert cleaned["Values"].max() < 100
    assert len(cleaned) == 8 # No rows removed

def test_minmax_scale(numeric_df):
    cleaned = minmax_scale(numeric_df, ["Scores"])
    assert cleaned["Scores"].min() == 0.0
    assert cleaned["Scores"].max() == 1.0

def test_zscore_scale(numeric_df):
    cleaned = zscore_scale(numeric_df, ["Scores"])
    assert np.isclose(cleaned["Scores"].mean(), 0.0, atol=1e-7)
    assert np.isclose(cleaned["Scores"].std(), 1.0, atol=1e-7)
