import pytest
import pandas as pd
from core.categorical_tools import (
    strip_whitespace, to_lowercase, to_titlecase, 
    map_categories, group_rare_categories, one_hot_encode
)

@pytest.fixture
def categorical_df():
    return pd.DataFrame({
        "Color": [" Red ", "BLuE ", "  green", "RED", "green", "pink"],
        "Size": ["Small", "Medium", "Large", "Medium", "Small", "Small"]
    })

def test_strip_whitespace(categorical_df):
    cleaned = strip_whitespace(categorical_df, "Color")
    assert cleaned["Color"].iloc[0] == "Red"
    assert cleaned["Color"].iloc[1] == "BLuE"
    assert cleaned["Color"].iloc[2] == "green"

def test_to_lowercase(categorical_df):
    # First strip to clean up
    df = strip_whitespace(categorical_df, "Color")
    cleaned = to_lowercase(df, "Color")
    assert cleaned["Color"].iloc[0] == "red"
    assert cleaned["Color"].iloc[1] == "blue"
    assert cleaned["Color"].iloc[3] == "red"

def test_to_titlecase(categorical_df):
    df = strip_whitespace(categorical_df, "Color")
    cleaned = to_titlecase(df, "Color")
    assert cleaned["Color"].iloc[0] == "Red"
    assert cleaned["Color"].iloc[1] == "Blue"
    assert cleaned["Color"].iloc[2] == "Green"

def test_map_categories(categorical_df):
    mapping = {"Small": "S", "Medium": "M", "Large": "L"}
    cleaned = map_categories(categorical_df, "Size", mapping)
    assert cleaned["Size"].iloc[0] == "S"
    assert cleaned["Size"].tolist() == ["S", "M", "L", "M", "S", "S"]
    
def test_group_rare_categories(categorical_df):
    # Color pink only appears once (1/6)
    cleaned = group_rare_categories(categorical_df, "Color", threshold=0.17) # 1/6 is ~16.6%
    assert cleaned["Color"].iloc[-1] == "Other"

def test_one_hot_encode(categorical_df):
    cleaned = one_hot_encode(categorical_df, "Size")
    assert "Size_Small" in cleaned.columns
    assert "Size_Medium" in cleaned.columns
    assert "Size_Large" in cleaned.columns
    assert "Size" not in cleaned.columns
    assert cleaned["Size_Medium"].iloc[1] == 1 # Second row is Medium
