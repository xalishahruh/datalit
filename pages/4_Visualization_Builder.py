import streamlit as st
import pandas as pd
from core.visualization_engine import (
    plot_histogram, plot_box, plot_scatter, 
    plot_line, plot_grouped_bar, plot_correlation_heatmap
)
from services.dataset_manager import get_dataset, dataset_exists, init_manager
from utils.ui_utils import apply_custom_styles

# Page Config
st.set_page_config(page_title="Visualization Builder", layout="wide")
apply_custom_styles()

# Initialize session state
init_manager()

st.title("📊 Visualization Builder")
st.markdown("---")

if not dataset_exists():
    st.warning("⚠️ Please upload a dataset first in the Data Upload page.")
    st.stop()

df = get_dataset()

# Sidebar: Dataset Slicing (Phase 3)
st.sidebar.header("🎯 Dataset Slicing")

# Categorical Filter
cat_cols = df.select_dtypes(exclude='number').columns.tolist()
if cat_cols:
    filter_col = st.sidebar.selectbox("Select Category Column", cat_cols)
    unique_vals = df[filter_col].unique().tolist()
    selected_vals = st.sidebar.multiselect(f"Filter {filter_col}", unique_vals, default=unique_vals)
    df_filtered = df[df[filter_col].isin(selected_vals)]
else:
    df_filtered = df.copy()

# Numeric Range Filter
num_cols = df.select_dtypes(include='number').columns.tolist()
if num_cols:
    range_col = st.sidebar.selectbox("Select Numeric Column", num_cols)
    min_val = float(df[range_col].min())
    max_val = float(df[range_col].max())
    selected_range = st.sidebar.slider(
        f"Range for {range_col}", 
        min_val, max_val, (min_val, max_val)
    )
    df_filtered = df_filtered[
        (df_filtered[range_col] >= selected_range[0]) & 
        (df_filtered[range_col] <= selected_range[1])
    ]

# Layout: 2 Columns for Controls vs Plot
ctrl_col, plot_col = st.columns([1, 2])

with ctrl_col:
    st.subheader("🛠️ Chart Configuration")
    
    # Rule-Based Chart Recommendations
    with st.expander("💡 Chart Recommendations"):
        st.write("Based on your dataset's schema, we recommend:")
        if len(num_cols) >= 2:
            st.markdown(f"- **Scatter Plot**: Good for comparing two continuous numeric variables (e.g., `{num_cols[0]}` vs `{num_cols[1]}`).")
        if len(num_cols) >= 1 and len(cat_cols) >= 1:
            st.markdown(f"- **Box Plot / Grouped Bar Chart**: Good for comparing a numeric variable (`{num_cols[0]}`) across categories (`{cat_cols[0]}`).")
        has_datetime = any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns)
        if has_datetime:
            st.markdown("- **Line Chart**: Highly recommended to observe trends over time.")
        if len(num_cols) >= 3:
            st.markdown("- **Correlation Heatmap**: Great for exploring relationships between multiple numeric features.")
    
    chart_type = st.selectbox(
        "Chart Type",
        [
            "Histogram",
            "Box Plot",
            "Scatter Plot",
            "Line Chart",
            "Grouped Bar Chart",
            "Correlation Heatmap"
        ]
    )

    fig = None
    
    if chart_type == "Histogram":
        if not num_cols:
            st.warning("⚠️ No numeric columns available for a Histogram.")
        else:
            col = st.selectbox("Select Numeric Column", num_cols)
            bins = st.slider("Bins", 5, 100, 20)
            if st.button("Generate Visualization"):
                with st.spinner("Generating Histogram..."):
                    fig = plot_histogram(df_filtered, col, bins)

    elif chart_type == "Box Plot":
        if not num_cols:
            st.warning("⚠️ No numeric columns available for a Box Plot.")
        else:
            y_col = st.selectbox("Numeric Variable (Y)", num_cols)
            x_col = st.selectbox("Grouping Variable (X) - Optional", ["None"] + df.columns.tolist())
            # Phase 4: Category Control
            top_n = st.slider("Top N Categories", 3, 50, 10)
            
            # Label rotation
            smart_rot = st.checkbox("Smart Rotation (Auto-tilt if long)", value=True, key="box_smart_rot")
            if smart_rot:
                rot = -1
            else:
                rot = st.slider("Manual Rotation", 0, 90, 0, step=15, key="box_rot")
            
            if st.button("Generate Visualization"):
                with st.spinner("Generating Box Plot..."):
                    plot_df = df_filtered.copy()
                    group_val = None
                    if x_col != "None":
                        # Handle datetime grouping by day for Top N
                        if pd.api.types.is_datetime64_any_dtype(plot_df[x_col]):
                            plot_df[x_col] = pd.to_datetime(plot_df[x_col]).dt.date
                        
                        top_categories = plot_df[x_col].value_counts().nlargest(top_n).index
                        plot_df = plot_df[plot_df[x_col].isin(top_categories)]
                        group_val = x_col
                    fig = plot_box(plot_df, y_col, group=group_val, rotation=rot)

    elif chart_type == "Scatter Plot":
        if len(num_cols) < 2:
            st.warning("⚠️ At least 2 numeric columns are required for a Scatter Plot.")
        else:
            x_col = st.selectbox("X Axis", num_cols)
            # Omit the column already selected for X from Y options
            y_options = [c for c in num_cols if c != x_col]
            y_col = st.selectbox("Y Axis (Numeric)", y_options)
            color_col = st.selectbox("Color Encoding - Optional", ["None"] + cat_cols)
            if st.button("Generate Visualization"):
                with st.spinner("Generating Scatter Plot..."):
                    hue = color_col if color_col != "None" else None
                    fig = plot_scatter(df_filtered, x_col, y_col, hue)

    elif chart_type == "Line Chart":
        x_col = st.selectbox("X Axis", df.columns)
        y_col = st.selectbox("Y Axis (Numeric)", num_cols)
        
        # Datetime detection and resampling
        is_datetime = pd.api.types.is_datetime64_any_dtype(df[x_col])
        resample_freq = None
        
        if is_datetime:
            st.info("✅ Datetime detected. You can group values to simplify the trend.")
            freq_map = {
                "Raw (No Grouping)": None,
                "Daily": "D",
                "Weekly": "W",
                "Monthly": "M",
                "Yearly": "Y"
            }
            freq_label = st.selectbox("Time Frequency", list(freq_map.keys()))
            resample_freq = freq_map[freq_label]
        else:
            st.warning("⚠️ X-axis is NOT a datetime column. Line charts work best with time-based data.")
            st.info("💡 You can convert columns to Datetime in the **Data Cleaning** page.")

        # Label rotation & Date format
        smart_rot = st.checkbox("Smart Rotation (Auto-tilt if long)", value=True, key="line_smart_rot")
        if smart_rot:
            rot = -1
        else:
            rot = st.slider("Manual Rotation", 0, 90, 45, step=15, key="line_rot")
            
        dt_fmt = None
        if is_datetime:
            dt_fmt = st.text_input("Date Format (e.g., %d/%m)", value="%d/%m/%y %H:%M", key="dt_fmt_input")

        if st.button("Generate Visualization"):
            with st.spinner("Generating Line Chart..."):
                plot_df = df_filtered.copy()
                if resample_freq:
                    # Group by time and take mean of Y
                    plot_df = plot_df.set_index(x_col).resample(resample_freq)[y_col].mean().reset_index()
                fig = plot_line(plot_df, x_col, y_col, rotation=rot, date_format=dt_fmt)

    elif chart_type == "Grouped Bar Chart":
        if not num_cols:
            st.warning("⚠️ No numeric columns available for aggregation.")
        elif not cat_cols:
            st.warning("⚠️ No categorical columns available for grouping.")
        else:
            x_col = st.selectbox("Category (X)", cat_cols)
            y_col = st.selectbox("Value (Y)", num_cols)
            agg_method = st.selectbox("Aggregation", ["mean", "sum", "count", "median"])
            # Phase 4: Category Control
            top_n = st.slider("Top N Categories", 3, 50, 10)
            
            # Label rotation
            smart_rot = st.checkbox("Smart Rotation (Auto-tilt if long)", value=True, key="bar_smart_rot")
            if smart_rot:
                rot = -1
            else:
                rot = st.slider("Manual Rotation", 0, 90, 45, step=15, key="bar_rot")
            
            if st.button("Generate Visualization"):
                with st.spinner("Generating Grouped Bar Chart..."):
                    top_categories = df_filtered[x_col].value_counts().nlargest(top_n).index
                    plot_df = df_filtered[df_filtered[x_col].isin(top_categories)]
                    fig = plot_grouped_bar(plot_df, x_col, y_col, agg_method, rotation=rot)

    elif chart_type == "Correlation Heatmap":
        with st.form("heatmap_form"):
            selected_num_cols = st.multiselect(
                "Select Columns for Heatmap", 
                num_cols, 
                default=num_cols[:10] # Default to first 10 to keep it readable
            )
            
            if st.form_submit_button("Generate Visualization"):
                with st.spinner("Computing Heatmap..."):
                    if len(selected_num_cols) < 2:
                        st.error("Please select at least 2 numeric columns.")
                    else:
                        fig = plot_correlation_heatmap(df_filtered[selected_num_cols])
                        if fig is None:
                            st.error("Correlation matrix could not be computed.")

with plot_col:
    st.subheader("📈 Preview")
    if fig:
        st.pyplot(fig)
    else:
        st.info("Adjust settings and click 'Generate Visualization' to see the chart.")