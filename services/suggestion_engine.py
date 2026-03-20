import pandas as pd
import numpy as np

def analyze_dataset(df):
    """
    Analyzes the dataframe and returns a list of prioritized suggestions.
    
    Structure of a suggestion:
    {
        "id": "unique_id",
        "title": "Suggestion Title",
        "description": "Suggestion Description",
        "severity": "critical|warning|info",
        "fix_action": "action_name",  # corresponds to a dataset_manager or core/transformations function
        "params": {},
        "auto_fixable": True/False
    }
    """
    suggestions = []
    
    # 1. Duplicates
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        suggestions.append({
            "id": "drop_duplicates",
            "title": "Remove Duplicate Rows",
            "description": f"Found {duplicate_count} duplicate rows in the dataset. Removing them will improve data quality.",
            "severity": "critical",
            "fix_action": "drop_duplicates",
            "params": {},
            "auto_fixable": True
        })
        
    # 2. Missing Values
    missing_data = df.isna().sum()
    for col in df.columns:
        m_count = missing_data[col]
        if m_count > 0:
            m_percent = (m_count / len(df)) * 100
            severity = "info"
            if m_percent > 50:
                severity = "critical"
                desc = f"Column '{col}' has {m_percent:.1f}% missing values. Consider dropping it."
                action = "drop_column"
            elif m_percent > 10:
                severity = "warning"
                desc = f"Column '{col}' has {m_percent:.1f}% missing values. Consider filling them."
                action = "fill_missing"
            else:
                desc = f"Column '{col}' has {m_percent:.1f}% missing values."
                action = "fill_missing"

            suggestions.append({
                "id": f"missing_{col}",
                "title": f"Handle Missing Values: {col}",
                "description": desc,
                "severity": severity,
                "fix_action": action,
                "params": {"column": col, "method": "median" if df[col].dtype in ['int64', 'float64'] else "mode"},
                "auto_fixable": True if severity != "critical" else False # Dropping columns should be a choice
            })

    # 3. Constant Columns (Single Unique Value)
    for col in df.columns:
        if df[col].nunique() == 1:
            suggestions.append({
                "id": f"constant_{col}",
                "title": f"Remove Constant Column: {col}",
                "description": f"Column '{col}' contains only one unique value: '{df[col].iloc[0]}'. It adds no information.",
                "severity": "info",
                "fix_action": "drop_column",
                "params": {"column": col},
                "auto_fixable": True
            })

    # 4. Outliers (Numeric Columns Only)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Simple IQR method
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_count = len(outliers)
        
        if outlier_count > 0:
            outlier_percent = (outlier_count / len(df)) * 100
            if outlier_percent > 5:
                suggestions.append({
                    "id": f"outliers_{col}",
                    "title": f"Handle Outliers: {col}",
                    "description": f"Column '{col}' has {outlier_count} outliers ({outlier_percent:.1f}% of data). Consider investigating or capping them.",
                    "severity": "warning",
                    "fix_action": "cap_outliers",
                    "params": {"column": col, "method": "clip"},
                    "auto_fixable": False
                })

    # Sort by severity (Critical > Warning > Info)
    severity_map = {"critical": 0, "warning": 1, "info": 2}
    suggestions.sort(key=lambda x: severity_map[x["severity"]])
    
    return suggestions

def calculate_health_score(df):
    """
    Calculates a quick health score between 0 and 100 based on suggestions.
    """
    suggestions = analyze_dataset(df)
    if not suggestions:
        return 100
    
    deductions = 0
    for s in suggestions:
        if s["severity"] == "critical":
            deductions += 20
        elif s["severity"] == "warning":
            deductions += 10
        elif s["severity"] == "info":
            deductions += 2
            
    score = max(0, 100 - deductions)
    return score
