import pandas as pd
import numpy as np
import json
import io
import datetime
import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt

from core import pipeline

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
        "    df = df.copy()",
        "    # Step-by-step reproduction of the DataLit session"
    ]
    
    if not recipe_log:
        script.append("    pass")
    else:
        for step in recipe_log:
            op = step.get('operation', 'Unknown')
            script.append(f"    # Operation: {op}")
            step_code = pipeline.get_step_python_code(step)
            script.append(step_code)
            
    script.append("    return df")
    script.append("")
    script.append("# --- Example Usage ---")
    script.append("# df = pd.read_csv('your_data.csv')")
    script.append("# clean_df = apply_recipe(df)")
    script.append("# print(clean_df.head())")
    
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
    pdf.set_font("Helvetica", 'B', 20)
    pdf.set_text_color(108, 92, 231) # DataLit Primary Color
    pdf.cell(0, 15, "DataLit Analysis Report", 0, 1, 'C')
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Dataset Overview
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(45, 52, 54)
    pdf.cell(0, 10, "1. Dataset Overview", 0, 1, 'L')
    pdf.set_font("Helvetica", '', 11)
    
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

