import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

from unittest.mock import MagicMock
import sys

# Mock streamlit before importing services
st_mock = MagicMock()
# Simple decorator that returns the function
st_mock.cache_data = lambda f=None, **kwargs: (lambda x: x) if f is None else f
sys.modules["streamlit"] = st_mock


# Add project root to path
sys.path.append(os.getcwd())

from services import export_service

def test_exports():
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['x', 'y', 'z'],
        'C': [10.5, 20.1, 15.2]
    })
    
    # Test CSV
    csv_bytes = export_service.export_as_csv(df)
    assert len(csv_bytes) > 0
    print("CSV Export: OK")
    
    # Test JSON
    json_bytes = export_service.export_as_json(df)
    assert len(json_bytes) > 0
    print("JSON Export: OK")
    
    # Test Image
    fig, ax = plt.subplots()
    ax.plot(df['A'], df['C'])
    img_bytes = export_service.export_as_image(fig)
    assert len(img_bytes) > 0
    print("Image Export: OK")
    
    # Test PDF
    summary = "Test Summary Stats"
    pdf_bytes = export_service.generate_pdf_report(summary, [img_bytes])
    assert len(pdf_bytes) > 0
    print("PDF Export: OK")

if __name__ == "__main__":
    try:
        test_exports()
        print("\nAll export tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        sys.exit(1)
