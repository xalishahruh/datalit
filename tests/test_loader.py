import pandas as pd
import io
import json
from core import loader

def test_load_csv():
    csv_data = "A,B\n1,2\n3,4"
    file = io.StringIO(csv_data)
    df = loader.load_dataset(file, "csv")
    assert df.shape == (2, 2)
    assert list(df.columns) == ['A', 'B']

def test_load_json():
    json_data = [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
    file = io.StringIO(json.dumps(json_data))
    df = loader.load_dataset(file, "json")
    assert df.shape == (2, 2)
    assert df['A'][0] == 1

def test_gsheets_url_conversion(monkeypatch):
    # Mocking pd.read_csv so it doesn't try a real network call
    def mock_read_csv(url):
        return pd.DataFrame({"dummy": [1]})
    
    monkeypatch.setattr(pd, "read_csv", mock_read_csv)
    
    url_edit = "https://docs.google.com/spreadsheets/d/123/edit#gid=0"
    df = loader.load_dataset(url_edit, "gsheets")
    assert not df.empty
    assert df.columns[0] == "dummy"
