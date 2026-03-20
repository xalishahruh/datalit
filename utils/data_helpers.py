import pandas as pd
import hashlib

def generate_dataset_hash(df: pd.DataFrame) -> str:
    """
    Generates a fast, unique hash for a dataframe based on its shape, 
    columns, and a small deterministic sample of data.
    """
    if df is None or df.empty:
        return "empty_df"
        
    # We use shape and columns as primary identity
    identity_str = f"{df.shape[0]}_{df.shape[1]}_{','.join(df.columns)}"
    
    # Sample up to 5 rows to catch internal data changes deterministically
    sample_size = min(5, len(df))
    sample_str = str(df.sample(n=sample_size, random_state=42).values.tolist())
    
    raw_hash = f"{identity_str}|{sample_str}".encode('utf-8')
    return hashlib.md5(raw_hash).hexdigest()
