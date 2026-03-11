import pytest
import pandas as pd
import streamlit as st
from services.dataset_manager import (
    init_manager, store_dataset, get_dataset, add_transformation,
    undo_transformation, reset_dataset, reset_session, dataset_exists
)

# Mocking Streamlit session state
class MockSessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

@pytest.fixture(autouse=True)
def mock_streamlit_session_state(monkeypatch):
    """Mocks st.session_state before each test."""
    mock_state = MockSessionState()
    monkeypatch.setattr(st, "session_state", mock_state)
    yield mock_state

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "A": [1, 2, 3],
        "B": ["x", "y", "z"]
    })

def test_init_manager():
    init_manager()
    assert getattr(st.session_state, "df", "missing") is None
    assert getattr(st.session_state, "original_df", "missing") is None
    assert getattr(st.session_state, "history", "missing") == []
    assert getattr(st.session_state, "recipe_log", "missing") == []
    assert getattr(st.session_state, "uploader_key", "missing") == 0

def test_dataset_exists_and_store_dataset(sample_df):
    init_manager()
    assert not dataset_exists()
    
    store_dataset(sample_df)
    assert dataset_exists()
    
    # Check if loaded properly
    df = get_dataset()
    pd.testing.assert_frame_equal(df, sample_df)
    assert len(st.session_state.history) == 1
    
def test_add_transformation(sample_df):
    init_manager()
    store_dataset(sample_df)
    
    # Create a modified dataframe
    new_df = sample_df.copy()
    new_df["A"] = new_df["A"] * 2
    
    add_transformation("Multiply A by 2", {"multiplier": 2}, ["A"], new_df)
    
    assert len(st.session_state.history) == 2
    assert len(st.session_state.recipe_log) == 1
    assert st.session_state.recipe_log[0]["operation"] == "Multiply A by 2"
    
    current_df = get_dataset()
    pd.testing.assert_frame_equal(current_df, new_df)

def test_undo_transformation(sample_df):
    init_manager()
    store_dataset(sample_df)
    
    new_df = sample_df.copy()
    new_df["A"] = new_df["A"] * 2
    add_transformation("Step 1", {}, ["A"], new_df)
    
    assert len(st.session_state.history) == 2
    
    # Undo it
    assert undo_transformation() is True
    assert len(st.session_state.history) == 1
    pd.testing.assert_frame_equal(get_dataset(), sample_df)
    
    # Cannot undo original state
    assert undo_transformation() is False

def test_reset_dataset(sample_df):
    init_manager()
    store_dataset(sample_df)
    
    new_df = sample_df.copy()
    new_df["A"] = new_df["A"] * 2
    add_transformation("Step 1", {}, ["A"], new_df)
    
    reset_dataset()
    assert len(st.session_state.history) == 1
    pd.testing.assert_frame_equal(get_dataset(), sample_df)
    assert len(st.session_state.recipe_log) == 0

def test_reset_session(sample_df):
    init_manager()
    store_dataset(sample_df)
    reset_session()
    
    # Session state is cleared, so 'df' and 'original_df' should not exist
    assert getattr(st.session_state, "df", "missing") == "missing"
    assert getattr(st.session_state, "original_df", "missing") == "missing"
    assert getattr(st.session_state, "history", "missing") == "missing"
