import pytest
import pandas as pd
from core.validation import (
    range_check, allowed_categories, non_null_violation
)

@pytest.fixture
def validation_df():
    return pd.DataFrame({
        "Age": [10, 25, 40, -5, 120],
        "Role": ["Admin", "User", "Guest", "Unknown", None],
        "Email": ["a@b.com", "c@d.com", None, "e@f.com", "g@h.com"]
    })

def test_range_check(validation_df):
    violations = range_check(validation_df, "Age", 0, 100)
    assert len(violations) == 2
    assert -5 in violations["Age"].tolist()
    assert 120 in violations["Age"].tolist()

def test_allowed_categories(validation_df):
    allowed = ["Admin", "User", "Guest"]
    violations = allowed_categories(validation_df, "Role", allowed)
    # Both "Unknown" and None (if considered string or float by pandas depending on parsing) 
    # will fail the allowed category check if not explicitly in `allowed`
    # Our function checks `~df[col].isin(allowed)` length
    filtered = validation_df[~validation_df["Role"].isin(allowed)]
    assert len(violations) == len(filtered)
    assert "Unknown" in violations["Role"].tolist()

def test_non_null_violation(validation_df):
    violations = non_null_violation(validation_df, "Email")
    assert len(violations) == 1
    assert violations["Email"].iloc[0] is None
