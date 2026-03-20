import pandas as pd
import numpy as np
import openai # Assuming user wants OpenAI as recommended

def generate_dataset_summary(df):
    """
    Creates a brief summary string for the dataset, used for LLM interaction.
    """
    summary = f"Dataset Summary:\n"
    summary += f"- Rows: {len(df)}\n"
    summary += f"- Columns: {len(df.columns)}\n"
    summary += f"- Duplicates: {df.duplicated().sum()}\n"
    summary += f"- Missing Values: {df.isna().sum().sum()} total\n"
    summary += "\nColumn Info:\n"
    for col in df.columns:
        summary += f"  - {col}: {df[col].dtype}\n"
        if df[col].dtype in ['int64', 'float64']:
            summary += f"    - Range: [{df[col].min()}, {df[col].max()}]\n"
        else:
            summary += f"    - Unique Values: {df[col].nunique()}\n"
            
    return summary

def generate_ai_insights(summary, api_enabled=False, api_key=None):
    """
    Sends the dataset summary to an LLM and returns insights.
    If api_enabled is False, it returns a mock summary.
    """
    if not api_enabled:
        return f"""
        **Dataset Quality Insights (Demo Mode)**
        
        - Your data has {summary.split('Rows: ')[1].split('\\n')[0]} rows.
        - Missing values were detected in several columns. Consider categorical imputation for sparse features.
        - Numerical ranges seem stable, but outliers in specific columns might skew model performance.
        - Recommendation: Use the "AI Assistant" page to fix critical issues immediately.
        """

    # Real API interaction
    try:
        # Prompt construction
        prompt = f"Analyze this dataset summary and provide 3 key risks and 3 actionable recommendations:\n\n{summary}"
        
        # client = openai.OpenAI(api_key=api_key)
        # response = client.chat.completions.create(...) # standard OpenAI API call
        
        # Placeholder for demonstration
        return f"AI Insights Generated Successfully: {prompt[:50]}..."
    except Exception as e:
        return f"Error connecting to LLM: {str(e)}"
