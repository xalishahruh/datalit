import pandas as pd

def load_csv (file):
    return pd.read_csv(file)

def load_excel (file):
    return pd.read_excel(file)

def load_json (file):
    return pd.read_json(file)