import pandas as pd
import numpy as np
import openai

def generate_dataset_summary(df):
    """
    Creates a comprehensive summary string for the dataset, used for LLM interaction.
    Includes data types, ranges, sample values, and statistical distributions.
    """
    summary = f"Dataset Analysis Summary:\n"
    summary += f"- Dimensions: {len(df)} rows x {len(df.columns)} columns\n"
    summary += f"- Duplicate Rows: {df.duplicated().sum()}\n"
    summary += f"- Global Missing Values: {df.isna().sum().sum()} cells ({ (df.isna().sum().sum() / (df.size)) * 100:.1f}%)\n"
    
    summary += "\nDetailed Column Profiling:\n"
    for col in df.columns:
        dtype = str(df[col].dtype)
        missing = df[col].isna().sum()
        unique_count = df[col].nunique()
        
        summary += f"\n- {col} ({dtype}):\n"
        summary += f"  - Missing: {missing} ({ (missing/len(df))*100:.1f}%)\n"
        summary += f"  - Uniques: {unique_count}\n"
        
        if pd.api.types.is_numeric_dtype(df[col]):
            stats = df[col].describe()
            summary += f"  - Stats: Mean={stats['mean']:.2f}, Std={stats['std']:.2f}, Range=[{stats['min']}, {stats['max']}]\n"
            summary += f"  - Quants: 25%={stats['25%']:.2f}, 50%={stats['50%']:.2f}, 75%={stats['75%']:.2f}\n"
        else:
            top_vals = df[col].value_counts().head(3).index.tolist()
            summary += f"  - Top 3 values: {', '.join([str(v) for v in top_vals])}\n"
            
    return summary

def generate_ai_insights(summary, api_enabled=False, api_key=None, model="gpt-4o-mini"):
    """
    Sends the dataset summary to an LLM and returns structured quality insights.
    If api_enabled is False or api_key is missing, it returns demo insights.
    """
    if not api_enabled or not api_key:
        return f"""
        ### 🤖 Data Quality Insights (Demo Mode)
        
        To see live AI-generated results, please provide your **OpenAI API Key** in the sidebar.
        
        **Preliminary Observations:**
        - **Scale**: A dataset of {summary.split('rows x')[0].split('Dimensions: ')[1]} rows provides sufficient statistical significance for most analysis.
        - **Missing Values**: Total missingness is {summary.split('Global Missing Values: ')[1].split('\\n')[0]}. High missingness in key features may require imputation strategies (mean/median for numeric, mode for categorical).
        - **Integrity**: {summary.split('- Duplicate Rows: ')[1].split('\\n')[0]} duplicate rows found. Removing these is highly recommended to avoid bias.
        
        **Recommendations:**
        1. Review the "AI Assistant" suggestions feed to apply one-click fixes.
        2. Inspect outliers in numeric columns using the **Data Profiler**.
        3. Standardize categorical text (casing/whitespace) to improve grouping.
        """

    try:
        client = openai.OpenAI(api_key=api_key)
        
        system_prompt = """
        You are an expert Data Scientist. Analyze the dataset summary and provide:
        
        [SUMMARY]
        A high-level executive summary of the dataset's quality and potential (1-2 sentences).
        
        [RISKS]
        List 3 critical data quality or integrity risks. Format each as: 
        - **Risk Title**: Description of the risk and potential impact.
        
        [RECOMMENDATIONS]
        List 3 actionable strategic recommendations. Format each as:
        - **Action Title**: Step-by-step or detailed recommendation.
        
        CRITICAL: Do not use any other headers. Use exactly [SUMMARY], [RISKS], [RECOMMENDATIONS] as separators.
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this dataset profile and provide deep insights:\n\n{summary}"}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"### ❌ Error Generating Insights\n\nFailed to connect to the external AI service.\n**Reason:** {str(e)}"
