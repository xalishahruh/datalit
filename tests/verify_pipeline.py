import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core import pipeline, transformations, column_ops

def test_pipeline():
    # 1. Create dummy data
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4],
        'B': ['  hello ', 'WORLD', 'foo', 'bar'],
        'C': [10, 20, 30, 40]
    })
    
    print("Original DataFrame:")
    print(df)
    
    # 2. Define a recipe
    recipe = [
        {"operation": "Remove Missing Rows", "parameters": {"option": "Remove from all columns"}},
        {"operation": "Text Cleaning", "parameters": {"column": "B", "operations": ["Strip Whitespace", "Lowercase"]}},
        {"operation": "Rename Column", "parameters": {"old": "C", "new": "D"}}
    ]
    
    # 3. Apply recipe
    print("\nApplying recipe...")
    clean_df = pipeline.apply_recipe(df, recipe)
    
    print("\nCleaned DataFrame:")
    print(clean_df)
    
    # 4. Assertions
    assert len(clean_df) == 3, "Should have removed 1 row"
    assert clean_df['B'].iloc[0] == 'hello', "Text cleaning failed"
    assert 'D' in clean_df.columns, "Rename failed"
    assert 'C' not in clean_df.columns, "Old column still exists"
    
    print("\n✅ Pipeline verification successful!")

    # 5. Check script generation
    print("\nTesting script generation...")
    for step in recipe:
        code = pipeline.get_step_python_code(step)
        print(f"Code for {step['operation']}:\n{code}")

if __name__ == "__main__":
    test_pipeline()
