import streamlit as st
import pandas as pd
from core.visualization_engine import (
    create_histogram, create_boxplot, create_scatter, 
    create_line, create_bar, create_heatmap
)
from utils.ui_utils import apply_custom_styles

st.set_page_config(page_title="Visualization Builder", layout="wide")
apply_custom_styles()

st.title("📊 Visualization Builder")

if "working_df" not in st.session_state or st.session_state.working_df is None:
    st.warning("Please upload a dataset first!")
    st.stop()

df = st.session_state.working_df

# Sidebar - Filtering
st.sidebar.header("🔍 Global Filters")
filtered_df = df.copy()

num_cols = df.select_dtypes(include=['number']).columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist() # Added 'bool' for categorical

for col in cat_cols:
    options = df[col].unique().tolist()
    selected = st.sidebar.multiselect(f"Filter {col}", options, default=options)
    if selected:
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

for col in num_cols:
    min_val, max_val = float(df[col].min()), float(df[col].max())
    # Fixed: check if min_val and max_val are same to avoid Slider error
    if min_val < max_val:
        range_val = st.sidebar.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
        filtered_df = filtered_df[(filtered_df[col] >= range_val[0]) & (filtered_df[col] <= range_val[1])]

# Main UI
col_opts, col_plot = st.columns([1, 2])

with col_opts:
    st.subheader("Chart Options")
    chart_type = st.selectbox("Select Chart Type", 
                              ["Histogram", "Box Plot", "Scatter Plot", "Line Chart", "Grouped Bar", "Correlation Heatmap"])
    
    fig = None
    
    if chart_type == "Histogram":
        x_col = st.selectbox("Column", num_cols + cat_cols)
        bins = st.slider("Number of Bins", 5, 100, 20)
        if st.button("Generate Histogram"):
            fig = create_histogram(filtered_df, x_col, bins, f"Histogram of {x_col}")
            
    elif chart_type == "Box Plot":
        y_col = st.selectbox("Y Axis (Numeric)", num_cols)
        x_col = st.selectbox("X Axis (Categorical, optional)", [None] + cat_cols)
        if st.button("Generate Box Plot"):
            fig = create_boxplot(filtered_df, x_col if x_col else y_col, y_col if x_col else None, f"Box Plot of {y_col}")
            
    elif chart_type == "Scatter Plot":
        x_col = st.selectbox("X Axis", num_cols)
        y_col = st.selectbox("Y Axis", num_cols)
        color_col = st.selectbox("Color By (optional)", [None] + cat_cols)
        if st.button("Generate Scatter Plot"):
            fig = create_scatter(filtered_df, x_col, y_col, color_col, f"Scatter: {x_col} vs {y_col}")
            
    elif chart_type == "Line Chart":
        x_col = st.selectbox("X Axis (Time/Numeric)", df.columns.tolist())
        y_col = st.selectbox("Y Axis", num_cols)
        group_col = st.selectbox("Group By (optional)", [None] + cat_cols)
        if st.button("Generate Line Chart"):
            fig = create_line(filtered_df, x_col, y_col, group_col, f"Line Chart: {y_col} over {x_col}")
            
    elif chart_type == "Grouped Bar":
        x_col = st.selectbox("X Axis (Categorical)", cat_cols)
        y_col = st.selectbox("Y Axis (Numeric)", num_cols)
        group_col = st.selectbox("Group By (optional)", [None] + cat_cols)
        agg_func = st.selectbox("Aggregation", ["mean", "sum", "count", "median", "min", "max"])
        if st.button("Generate Bar Chart"):
            fig = create_bar(filtered_df, x_col, y_col, agg_func, group_col, f"{agg_func.title()} of {y_col} by {x_col}")
            
    elif chart_type == "Correlation Heatmap":
        if st.button("Generate Heatmap"):
            fig = create_heatmap(filtered_df, "Correlation Matrix")

with col_plot:
    st.subheader("Visualization Output")
    if fig:
        st.pyplot(fig)
    else:
        st.info("Configuration is ready. Click 'Generate' to see the chart.")

st.divider()
st.write(f"Showing results for {len(filtered_df)} rows after filtering.")
