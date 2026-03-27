import pandas as pd
from core import pipeline

def test_pipeline_mapping():
    steps = [
        {"operation": "Remove Duplicate Rows", "parameters": {"subset": "full", "type": "First"}},
        {"operation": "Handle Outliers: Age", "parameters": {"column": "Age", "action": "Cap outliers"}},
        {"operation": "Fill Missing Values", "parameters": {"column": "Salary", "method": "Mean"}},
        {"operation": "Rename Column", "parameters": {"old": "A", "new": "B"}},
        {"operation": "Create Formula Column", "parameters": {"name": "Total", "formula": "A + B"}},
        {"operation": "Quantile Binning", "parameters": {"column": "Age", "bins": 5}}
    ]
    
    print("--- Testing Pipeline Mapping ---")
    for step in steps:
        code = pipeline.get_step_python_code(step)
        print(f"Op: {step['operation']}")
        print(f"Code:\n{code}")
        assert "# TODO" not in code, f"Mapping failed for {step['operation']}"
    print("--- All Mappings Verified! ---")

if __name__ == "__main__":
    test_pipeline_mapping()
