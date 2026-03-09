import sys
import os
import pandas as pd
import io

# Ensure the project root is in sys.path
sys.path.append(os.getcwd())

from core.loader import load_dataset

# Simple mock for testing
class MockFile(io.BytesIO):
    def __init__(self, content, name):
        super().__init__(content)
        self.name = name

def test_loader():
    print("Testing loader with CSV...")
    
    with open("test_data.csv", "rb") as f:
        file_obj = MockFile(f.read(), "test_data.csv")
        try:
            df = load_dataset(file_obj)
            print("Successfully loaded CSV:")
            print(df.head(2))
            assert not df.empty
            print("✅ CSV Test Passed")
        except Exception as e:
            print(f"❌ CSV Test Failed: {e}")

if __name__ == "__main__":
    test_loader()
