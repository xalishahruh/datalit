import pandas as pd
import numpy as np
import json
import io
import datetime
import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt

def generate_python_script(recipe_log):
    """
    Converts the transformation recipe log into a standalone Python script.
    """
    script = [
        "import pandas as pd",
        "import numpy as np",
        "from core import transformations, numeric_tools, categorical_tools, column_ops",
        "",
        "def apply_recipe(df):",
        "    \"\"\"Applies the saved transformation recipe to a dataframe.\"\"\"",
        "    new_df = df.copy()"
    ]
    
    for step in recipe_log:
        op = step['operation']
        params = step['parameters']
        
        script.append(f"    # Step: {op}")
        
        if "Remove Missing Rows" in op:
            if params.get('option') == "Remove from all columns":
                script.append("    new_df = transformations.drop_missing_rows(new_df)")
            else:
                script.append(f"    new_df = transformations.drop_missing_rows(new_df, {params.get('columns')})")
        
        elif "Fill Missing" in op:
            method = params.get('method', '').lower()
            col = params.get('column')
            if method in ['mean', 'median']:
                script.append(f"    new_df = transformations.fill_numeric(new_df, '{col}', '{method}')")
            elif 'mode' in method:
                script.append(f"    new_df = transformations.fill_mode(new_df, '{col}')")
            elif method == 'constant':
                script.append(f"    new_df = transformations.fill_constant(new_df, '{col}', '{params.get('value')}')")
        
        elif "Remove Duplicates" in op:
            subset = params.get('subset')
            keep = params.get('type', 'First').lower()
            script.append(f"    new_df = transformations.remove_duplicates(new_df, subset={None if subset == 'full' else subset}, keep='{keep}')")
            
        elif "Drop Column" in op:
            script.append(f"    new_df = column_ops.drop_column(new_df, '{params.get('column')}')")
            
        elif "Rename Column" in op:
            script.append(f"    new_df = column_ops.rename_column(new_df, '{params.get('old')}', '{params.get('new')}')")
            
        # Add more mappings as needed for other operations...
        else:
            script.append(f"    # TODO: Implement mapping for {op}")
            
    script.append("    return new_df")
    script.append("")
    script.append("# Example Usage:")
    script.append("# df = pd.read_csv('your_data.csv')")
    script.append("# clean_df = apply_recipe(df)")
    
    return "\n".join(script)

def export_as_csv(df):
    """Standardized CSV export optimized for Streamlit."""
    return df.to_csv(index=False).encode('utf-8')

def export_as_json(df):
    """Standardized JSON export optimized for Streamlit."""
    return df.to_json(orient="records", indent=4).encode('utf-8')

def export_as_excel(df):
    """Standardized Excel export using openpyxl, optimized for Streamlit."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cleaned Data')
    return buffer.getvalue()

def export_as_image(fig, format="png"):
    """Saves a matplotlib figure to bytes, optimized for Streamlit."""
    buf = io.BytesIO()
    fig.savefig(buf, format=format, bbox_inches='tight', dpi=300)
    buf.seek(0)
    return buf.getvalue()

@st.cache_data(show_spinner="Generating Professional PDF Report...")
def generate_pdf_report(df_summary_html, chart_bytes_list=None):
    """
    Generates a professional PDF report.
    df_summary_html: A string or dict representing the dataset summary.
    chart_bytes_list: List of bytes for images to include.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(108, 92, 231) # DataLit Primary Color
    pdf.cell(0, 15, "DataLit Analysis Report", 0, 1, 'C')
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Dataset Overview
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(45, 52, 54)
    pdf.cell(0, 10, "1. Dataset Overview", 0, 1, 'L')
    pdf.set_font("Arial", '', 11)
    
    # Simple summary stats instead of full HTML to PDF (fpdf2 is limited with HTML)
    pdf.multi_cell(0, 10, df_summary_html)
    pdf.ln(10)
    
    # Charts
    if chart_bytes_list:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "2. Visualizations", 0, 1, 'L')
        pdf.ln(5)
        
        for i, chart_bytes in enumerate(chart_bytes_list):
            # Use fpdf2's ability to take BytesIO
            img_stream = io.BytesIO(chart_bytes)
            pdf.image(img_stream, x=10, w=190)
            pdf.ln(10)
            if i < len(chart_bytes_list) - 1:
                pdf.add_page()
                
    return bytes(pdf.output())

