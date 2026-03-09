import sys
import os
import pandas as pd
import io

# Ensure the project root is in sys.path
sys.path.append(os.getcwd())

from core.loader import load_dataset
from core.profiling import get_missing_values, get_duplicates, get_summary_stats, get_inferred_dtypes

# Simple mock for testing
class MockFile(io.BytesIO):
    def __init__(self, content, name):
        super().__init__(content)
        self.name = name

def test_full_pipeline():
    print("Testing loader and profiling pipeline...")
    
    with open("test_data.csv", "rb") as f:
        file_obj = MockFile(f.read(), "test_data.csv")
        try:
            # 1. Load
            df = load_dataset(file_obj)
            print("- Load successful")
            
            # 2. Inferred Dtypes
            dtypes = get_inferred_dtypes(df)
            print("- Inferred types calculated")
            
            # 3. Missing values
            missing = get_missing_values(df)
            print("- Missing values calculated")
            
            # 4. Duplicates
            dupes = get_duplicates(df)
            print(f"- Duplicates found: {dupes}")
            
            # 5. Stats
            num_sum, cat_sum = get_summary_stats(df)
            print("- Summary stats generated")
            
            print("\n✅ Full Pipeline Test Passed!")
        except Exception as e:
            print(f"\n❌ Pipeline Test Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_full_pipeline()
