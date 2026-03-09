import pandas as pd
import os

def _load_csv(file):
    """Internal helper to load CSV with encoding fallback."""
    try:
        return pd.read_csv(file, on_bad_lines="skip", encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, on_bad_lines="skip", encoding="ISO-8859-1", low_memory=False)

def load_dataset(file):
    """
    Intelligently loads a dataset based on its file extension.
    Uses a dispatch mapping for efficient selection of the loader function.
    """
    ext = os.path.splitext(file.name)[1].lower()
    
    # Mapping of extensions to loading functions
    loaders = {
        ".csv": _load_csv,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".json": pd.read_json
    }

    loader_func = loaders.get(ext)
    
    if not loader_func:
        raise ValueError(f"The format '{ext}' is not supported. Please use CSV, Excel, or JSON.")

    try:
        if loader_func == _load_csv: # Special case for fallback logic
            return loader_func(file)
        return loader_func(file)
    except Exception as e:
        raise Exception(f"Error processing {file.name}: {str(e)}")

