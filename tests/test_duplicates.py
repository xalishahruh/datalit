import pytest
import pandas as pd
from core.transformations import (
    detect_duplicates, detect_duplicates_subset, remove_duplicates
)

@pytest.fixture
def duplicated_df():
    return pd.DataFrame({
        "ID": [1, 2, 3, 2, 4, 1],
        "Name": ["Alice", "Bob", "Charlie", "Bob", "David", "Alice"],
        "Age": [25, 30, 35, 30, 40, 25]
    })

@pytest.fixture
def subset_duplicated_df():
    return pd.DataFrame({
        "ID": [1, 2, 3, 4, 5, 6],
        "Name": ["Alice", "Bob", "Charlie", "Bob", "David", "Alice"],
        "Age": [25, 30, 35, 31, 40, 26]
    })

def test_detect_duplicates(duplicated_df):
    dups = detect_duplicates(duplicated_df)
    # Rows 1 and 2 are Alice, rows index 1 and 3 are Bob
    assert len(dups) == 4 # Both first and subsequent occurrences are highlighted by default 
    
def test_detect_duplicates_subset(subset_duplicated_df):
    # Only Name is duplicated
    dups = detect_duplicates_subset(subset_duplicated_df, ["Name"])
    assert len(dups) == 4

def test_remove_duplicates(duplicated_df):
    # Default keep='first'
    cleaned = remove_duplicates(duplicated_df)
    assert len(cleaned) == 4
    assert cleaned["ID"].tolist() == [1, 2, 3, 4]

    # Keep='last'
    cleaned_last = remove_duplicates(duplicated_df, keep='last')
    assert len(cleaned_last) == 4
    # The last occurrence of ID 1 is at index 5, ID 2 is at index 3
    assert cleaned_last["ID"].tolist() == [3, 2, 4, 1] 

def test_remove_duplicates_subset(subset_duplicated_df):
    cleaned = remove_duplicates(subset_duplicated_df, subset=["Name"])
    assert len(cleaned) == 4
    assert cleaned["Age"].tolist() == [25, 30, 35, 40] # Kept first occurrence Ages
