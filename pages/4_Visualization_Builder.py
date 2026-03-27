import streamlit as st
import pandas as pd
import json
import datetime
import io
from core.visualization_engine import (
    plot_histogram, plot_box, plot_scatter, 
    plot_line, plot_grouped_bar, plot_correlation_heatmap,
    plot_area, plot_pie
)
from services.dataset_manager import get_dataset, dataset_exists, init_manager
from services import export_service
from utils.ui_utils import apply_custom_styles

# Page Config
st.set_page_config(page_title="Visualization Builder Pro", layout="wide")
apply_custom_styles()

# Initialize session state
init_manager()
if 'viz_config' not in st.session_state:
    st.session_state.viz_config = {}
if 'user_role' not in st.session_state:
    st.session_state.user_role = "Business User"
if 'dashboard_charts' not in st.session_state:
    st.session_state.dashboard_charts = [] # Stores up to 6 charts

st.title("📊 Visualization Builder Pro")
st.markdown("---")

if not dataset_exists():
    st.warning("⚠️ Please upload a dataset first in the Data Upload page.")
    st.stop()

df = get_dataset()
num_cols = df.select_dtypes(include='number').columns.tolist()
cat_cols = df.select_dtypes(exclude='number').columns.tolist()

# Role Selector in Sidebar
with st.sidebar:
    st.header("👤 User Perspective")
    st.session_state.user_role = st.selectbox(
        "Select Your Role",
        ["Amateur", "Business User", "Analyst", "Engineer"],
        index=["Amateur", "Business User", "Analyst", "Engineer"].index(st.session_state.user_role if st.session_state.user_role in ["Amateur", "Business User", "Analyst", "Engineer"] else "Amateur")
    )
    st.info(f"Viewing as: **{st.session_state.user_role}**")
    
    st.markdown("---")
    st.header("🎯 Dataset Slicing")
    
    # Simple filters for all roles
    if cat_cols:
        filter_col = st.selectbox("Category Filter", cat_cols)
        unique_vals = df[filter_col].unique().tolist()
        selected_vals = st.multiselect(f"Selected {filter_col}", unique_vals, default=unique_vals[:5])
        df_filtered = df[df[filter_col].isin(selected_vals)]
    else:
        df_filtered = df.copy()

    # Dashboard Status in Sidebar
    st.markdown("---")
    st.header("📋 Dashboard Plate")
    slots_full = len(st.session_state.dashboard_charts)
    st.progress(slots_full / 6)
    st.write(f"**{slots_full}/6** charts saved to dashboard.")
    if slots_full > 0:
        if st.button("🚀 View Dashboard", use_container_width=True):
            st.toast("Scrolling to dashboard...")
            # Streamlit doesn't have an easy "scroll to" so this is just for UX

# Main Panel Layout
ctrl_col, plot_col = st.columns([1, 2])

with ctrl_col:
    st.subheader(f"🛠️ {st.session_state.user_role} Controls")
    
    # Rule-Based Chart Recommendations (Common tip)
    with st.expander("💡 Chart Recommendations"):
        st.write("Based on your dataset's schema, we recommend:")
        if len(num_cols) >= 2:
            st.markdown(f"- **Scatter Plot**: Good for comparing numeric `{num_cols[0]}` vs `{num_cols[1]}`.")
        if len(num_cols) >= 1 and len(cat_cols) >= 1:
            st.markdown(f"- **Box Plot**: Good for comparing `{num_cols[0]}` across categories `{cat_cols[0]}`.")
        has_datetime = any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns)
        if has_datetime:
            st.markdown("- **Line Chart**: Best for trends over time.")
    
    chart_type = None
    params = {}
    
    if st.session_state.user_role == "Amateur":
        st.markdown("#### 🔍 Data Quick Check")
        st.info("Pick a column and a style to see a quick snapshot.")
        quick_col = st.selectbox("Pick a column", num_cols + cat_cols)
        chart_type = st.selectbox("Choose Your Chart", ["Histogram", "Box Plot", "Scatter Plot", "Line Chart", "Grouped Bar Chart", "Correlation Heatmap"])
        
        if chart_type == "Histogram":
            params = {"column": quick_col, "bins": 15}
        elif chart_type == "Box Plot":
            params = {"y": quick_col if quick_col in num_cols else (num_cols[0] if num_cols else quick_col)}
        elif chart_type == "Grouped Bar Chart":
            params = {"x": quick_col, "y": num_cols[0] if num_cols else "", "agg": "count"}
        # Other types use defaults or simple logic
        elif chart_type == "Scatter Plot":
            params = {"x": quick_col if quick_col in num_cols else (num_cols[0] if num_cols else quick_col), "y": num_cols[0]}
        elif chart_type == "Line Chart":
            params = {"x": df.columns[0], "y": quick_col if quick_col in num_cols else (num_cols[0] if num_cols else quick_col)}

    elif st.session_state.user_role == "Business User":
        st.markdown("#### Quick Templates & Custom Choice")
        template = st.selectbox("Select Business KPI", ["Sales Trend", "Distribution Analysis", "Category Breakdown", "Custom / Choose My Own"])
        
        if template == "Custom / Choose My Own":
            chart_type = st.selectbox("Choose Your Chart", ["Histogram", "Box Plot", "Scatter Plot", "Line Chart", "Grouped Bar Chart", "Correlation Heatmap", "Area Chart", "Pie Chart"])
            col_x = st.selectbox("Dimension / Primary Axis", df.columns)
            col_y = st.selectbox("Metric / Secondary Axis", num_cols)
            params = {"x": col_x, "y": col_y, "column": col_x}
        
        elif template == "Sales Trend":
            date_col = st.selectbox("Date Column", df.columns)
            val_col = st.selectbox("Metric Column", num_cols)
            chart_type = st.radio("Visual Style", ["Line Chart", "Area Chart"], horizontal=True)
            params = {"x": date_col, "y": val_col}
            
        elif template == "Distribution Analysis":
            col = st.selectbox("Metric", num_cols)
            chart_type = st.radio("Visual Style", ["Histogram", "Box Plot"], horizontal=True)
            params = {"column": col, "bins": 20, "y": col}
            
        elif template == "Category Breakdown":
            cat = st.selectbox("Category", cat_cols)
            val = st.selectbox("Metric", num_cols)
            chart_type = st.radio("Visual Style", ["Grouped Bar Chart", "Pie Chart"], horizontal=True)
            params = {"x": cat, "y": val, "agg": "mean"}

    elif st.session_state.user_role == "Analyst":
        st.markdown("#### Advanced Configuration")
        chart_type = st.selectbox("Chart Type", ["Histogram", "Box Plot", "Scatter Plot", "Line Chart", "Area Chart", "Pie Chart", "Grouped Bar Chart", "Correlation Heatmap"])
        
        if chart_type == "Scatter Plot":
            params["x"] = st.selectbox("X Axis", num_cols)
            params["y"] = st.selectbox("Y Axis", [c for c in num_cols if c != params["x"]])
            params["color"] = st.selectbox("Color (Optional)", ["None"] + cat_cols)
        elif chart_type == "Grouped Bar Chart":
            params["x"] = st.selectbox("Category", cat_cols)
            params["y"] = st.selectbox("Metric", num_cols)
            params["agg"] = st.selectbox("Aggregation", ["mean", "sum", "count", "median"])
        elif chart_type == "Histogram":
            params["column"] = st.selectbox("Numeric Column", num_cols)
            params["bins"] = st.slider("Bins", 5, 100, 20)
        elif chart_type == "Box Plot":
            params["y"] = st.selectbox("Numeric Variable (Y)", num_cols)
            params["x"] = st.selectbox("Grouping Variable (X) - Optional", ["None"] + df.columns.tolist())
        elif chart_type == "Line Chart":
            params["x"] = st.selectbox("X Axis", df.columns)
            params["y"] = st.selectbox("Y Axis (Metric)", num_cols)
        elif chart_type == "Correlation Heatmap":
            params["selected_cols"] = st.multiselect("Columns", num_cols, default=num_cols[:10])

    elif st.session_state.user_role == "Engineer":
        st.markdown("#### Transformation & Direct Query")
        st.info("Directly edit visualization parameters via JSON.")
        if 'viz_config' not in st.session_state: st.session_state.viz_config = {"chart_type": "Histogram", "params": {"column": num_cols[0] if num_cols else ""}}
        config_json = st.text_area("Visualization Config (JSON)", value=json.dumps(st.session_state.viz_config, indent=2), height=200)
        try:
            cfg = json.loads(config_json)
            chart_type = cfg.get("chart_type", "Histogram")
            params = cfg.get("params", {})
        except:
            st.error("Invalid JSON format")
            chart_type = "Histogram"
            params = {}

    st.markdown("---")
    gen_btn = st.button("🚀 Generate Visualization", type="primary", use_container_width=True)
    save_btn = st.button("💾 Save Configuration", use_container_width=True)
    
    if save_btn:
        st.session_state.viz_config = {"chart_type": chart_type, "params": params}
        st.success("Configuration saved to session!")
fig = None
with plot_col:
    st.subheader("📈 Real-time Preview")
    
    if gen_btn or 'fig' in st.session_state:
        with st.spinner("Rendering..."):
            # Unified plotting logic
            if chart_type == "Histogram":
                fig = plot_histogram(df_filtered, params.get("column", num_cols[0]), params.get("bins", 20))
            elif chart_type == "Box Plot":
                fig = plot_box(df_filtered, params.get("y", num_cols[0]), group=params.get("x") if params.get("x") != "None" else None)
            elif chart_type == "Scatter Plot":
                fig = plot_scatter(df_filtered, params["x"], params["y"], params.get("color") if params.get("color") != "None" else None)
            elif chart_type == "Line Chart":
                fig = plot_line(df_filtered, params["x"], params["y"])
            elif chart_type == "Area Chart":
                fig = plot_area(df_filtered, params["x"], params["y"])
            elif chart_type == "Pie Chart":
                fig = plot_pie(df_filtered, params["x"], params["y"], params.get("agg", "sum"))
            elif chart_type == "Grouped Bar Chart":
                fig = plot_grouped_bar(df_filtered, params["x"], params["y"], params.get("agg", "mean"))
            elif chart_type == "Correlation Heatmap":
                fig = plot_correlation_heatmap(df_filtered)
            
            if fig:
                st.pyplot(fig)
                st.session_state.fig = fig
                
                # Dashboard Plate Logic
                st.markdown("---")
                if len(st.session_state.dashboard_charts) < 6:
                    if st.button(f"➕ Add to Dashboard ({len(st.session_state.dashboard_charts)}/6)", use_container_width=True):
                        chart_data = {"chart_type": chart_type, "params": params, "df_filtered": df_filtered.copy()}
                        st.session_state.dashboard_charts.append(chart_data)
                        st.toast("Chart added to your Dashboard Plate!", icon="✅")
                else:
                    st.warning("Dashboard Plate is full (6/6).")
            else:
                st.info("Select parameters and click 'Generate Visualization'.")

    # Export Section
    if 'fig' in st.session_state:
        st.markdown("---")
        st.subheader("📤 Export Options")
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        
        with exp_col1:
            st.info("🖼️ **PNG Chart**")
            img_bytes = export_service.export_as_image(st.session_state.fig)
            st.download_button("Download PNG", img_bytes, "chart.png", "image/png", use_container_width=True)
            
        with exp_col2:
            st.info("📋 **PDF Report**")
            # Generate a summary for the PDF
            summary_text = f"Dataset size: {df_filtered.shape}\nColumns: {', '.join(df_filtered.columns)}\n"
            pdf_bytes = export_service.generate_pdf_report(summary_text, [img_bytes])
            st.download_button("Download PDF", pdf_bytes, "report.pdf", "application/pdf", use_container_width=True)
            
        with exp_col3:
            st.info("🔗 **JSON Data**")
            data_json = export_service.export_as_json(df_filtered)
            st.download_button("Download JSON", data_json, "data.json", "application/json", use_container_width=True)

# --- Section 4: Dashboard Experience (Phase 6) ---
if st.session_state.dashboard_charts:
    st.markdown("---")
    st.header("🎨 Your Generated Dashboard")
    st.info("This is your live dashboard plate (max 6 charts).")
    
    if st.button("🗑️ Clear Dashboard", use_container_width=True):
        st.session_state.dashboard_charts = []
        st.rerun()

    # Create a 2-column grid
    cols = st.columns(2)
    for idx, chart in enumerate(st.session_state.dashboard_charts):
        with cols[idx % 2]:
            st.markdown(f"**Chart {idx + 1}: {chart['chart_type']}**")
            # Re-render the chart from saved params
            saved_type = chart['chart_type']
            saved_params = chart['params']
            saved_df = chart['df_filtered']
            
            with st.spinner(f"Loading chart {idx+1}..."):
                if saved_type == "Histogram":
                    f = plot_histogram(saved_df, saved_params["column"], saved_params.get("bins", 20))
                elif saved_type == "Box Plot":
                    f = plot_box(saved_df, saved_params["y"], saved_params.get("x"))
                elif saved_type == "Scatter Plot":
                    f = plot_scatter(saved_df, saved_params["x"], saved_params["y"], saved_params.get("color"))
                elif saved_type == "Line Chart":
                    f = plot_line(saved_df, saved_params["x"], saved_params["y"])
                elif saved_type == "Area Chart":
                    f = plot_area(saved_df, saved_params["x"], saved_params["y"])
                elif saved_type == "Pie Chart":
                    f = plot_pie(saved_df, saved_params["x"], saved_params["y"], saved_params.get("agg", "sum"))
                elif saved_type == "Grouped Bar Chart":
                    f = plot_grouped_bar(saved_df, saved_params["x"], saved_params["y"], saved_params.get("agg", "mean"))
                elif saved_type == "Correlation Heatmap":
                    f = plot_correlation_heatmap(saved_df)
                
                if f:
                    st.pyplot(f)
                    # Inline export for individual chart if needed
                    c1, c2 = st.columns(2)
                    with c1:
                        img = export_service.export_as_image(f)
                        st.download_button(f"PNG", img, f"chart_{idx+1}.png", "image/png", key=f"dl_{idx}")
                    with c2:
                        st.button("Remove", key=f"rm_{idx}", on_click=lambda i=idx: st.session_state.dashboard_charts.pop(i))

    st.markdown("---")
    st.subheader("🏁 Finalize & Export Report")
    if st.button("📥 Generate All-in-One PDF Report", type="primary", use_container_width=True):
        with st.spinner("Compiling multi-chart report..."):
            all_charts_bytes = []
            for chart in st.session_state.dashboard_charts:
                # Re-render to get fig
                saved_type = chart['chart_type']
                saved_params = chart['params']
                saved_df = chart['df_filtered']
                f = None
                if saved_type == "Histogram":
                    f = plot_histogram(saved_df, saved_params["column"], saved_params.get("bins", 20))
                elif saved_type == "Box Plot":
                    f = plot_box(saved_df, saved_params["y"], saved_params.get("x"))
                elif saved_type == "Scatter Plot":
                    f = plot_scatter(saved_df, saved_params["x"], saved_params["y"], saved_params.get("color"))
                elif saved_type == "Line Chart":
                    f = plot_line(saved_df, saved_params["x"], saved_params["y"])
                elif saved_type == "Area Chart":
                    f = plot_area(saved_df, saved_params["x"], saved_params["y"])
                elif saved_type == "Pie Chart":
                    f = plot_pie(saved_df, saved_params["x"], saved_params["y"], saved_params.get("agg", "sum"))
                elif saved_type == "Grouped Bar Chart":
                    f = plot_grouped_bar(saved_df, saved_params["x"], saved_params["y"], saved_params.get("agg", "mean"))
                elif saved_type == "Correlation Heatmap":
                    f = plot_correlation_heatmap(saved_df)
                
                if f:
                    all_charts_bytes.append(export_service.export_as_image(f))
            
            summary_text = f"Consolidated Dashboard Report\nCharts included: {len(all_charts_bytes)}\nGeneration Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            pdf_bytes = export_service.generate_pdf_report(summary_text, all_charts_bytes)
            st.download_button("Download Dashboard PDF", pdf_bytes, "dashboard_report.pdf", "application/pdf", use_container_width=True)

# Footer: Business Alignment Tips
with st.expander("💡 Business Insights & Monitoring Tip"):
    st.markdown("""
    - **KPI Tracking**: Use the 'Business User' role to quickly monitor sales and performance trends.
    - **Operational Monitoring**: Analysts can use 'Scatter Plots' to detect anomalies in process metrics.
    - **Custom Logic**: Engineers can use the JSON config to build proprietary visualization pipelines.
    """)

