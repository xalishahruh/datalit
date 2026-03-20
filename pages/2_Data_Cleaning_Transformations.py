import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json
import openpyxl  

# Import your existing modules - FIXED PATHS
from core.categorical_tools import (
    strip_whitespace, to_lowercase, to_titlecase, 
    map_categories, group_rare_categories, one_hot_encode
)
from core.column_ops import (
    rename_column, drop_column, create_formula_column,
    equal_width_bins, quantile_bins
)
from core.numeric_tools import (
    detect_outliers_iqr, cap_outliers, remove_outliers,
    minmax_scale, zscore_scale
)
from core.transformations import (
    drop_missing_rows, drop_columns_by_threshold, fill_constant,
    fill_numeric, fill_mode, fill_forward, fill_backward,
    detect_duplicates, detect_duplicates_subset, remove_duplicates,
    clean_numeric_strings, convert_to_numeric, convert_to_datetime,
    convert_to_category
)
from core.validation import range_check, allowed_categories, non_null_violation

# Import dataset manager functions
from services.dataset_manager import (
    add_transformation, get_dataset, undo_transformation,
    reset_dataset, reset_session, dataset_exists, init_manager
)

# 1. Initialize state
init_manager()

def show_transformation_page():
    """Main transformation/cleaning page"""
    
    st.title("Data Cleaning & Transformation")
    
    if not dataset_exists():
        st.info("Please upload a dataset first on the Overview page to begin cleaning.")
        return
    
    df = get_dataset().copy()
    
    # Create tabs for different transformation categories
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Missing Values", 
        "🔄 Duplicates", 
        "🏷️ Categorical", 
        "🔢 Numeric", 
        "📅 Data Types",
        "📏 Column Ops",
        "✅ Validation"
    ])
    
    with tab1:
        show_missing_values_tab(df)
    
    with tab2:
        show_duplicates_tab(df)
    
    with tab3:
        show_categorical_tab(df)
    
    with tab4:
        show_numeric_tab(df)
    
    with tab5:
        show_datatype_tab(df)
    
    with tab6:
        show_column_ops_tab(df)
    
    with tab7:
        show_validation_tab(df)
    
    # Show transformation log at the bottom
    show_transformation_log()

def render_preview_metrics(df_before, df_after, affected_cols):
    """Render before/after metrics for a transformation"""
    st.markdown("#### 🔍 Transformation Preview")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Rows Before", len(df_before))
        st.metric("Rows After", len(df_after), delta=len(df_after) - len(df_before))
    
    with c2:
        missing_before = df_before[affected_cols].isna().sum().sum() if affected_cols else df_before.isna().sum().sum()
        missing_after = df_after[affected_cols].isna().sum().sum() if affected_cols else df_after.isna().sum().sum()
        st.metric("Total Missing (Affected)", missing_before)
        st.metric("Remaining Missing", missing_after, delta=int(missing_after - missing_before))
        
    with c3:
        st.info(f"**Affected Columns:**\n{', '.join(affected_cols[:5])}{'...' if len(affected_cols) > 5 else ''}")

    with st.expander("👀 View Data Sample (First 5 Rows)"):
        st.markdown("**Before:**")
        st.dataframe(df_before.head(5), use_container_width=True)
        st.markdown("**After:**")
        st.dataframe(df_after.head(5), use_container_width=True)

def show_missing_values_tab(df):
    """🎯 Missing Values Handling"""
    st.markdown("### 🎯 Missing Values Management")
    
    # Display missing values summary
    missing_df = pd.DataFrame({
        'Column': df.columns,
        'Missing Count': df.isna().sum().values,
        'Missing %': (df.isna().sum().values / len(df) * 100).round(2)
    }).sort_values('Missing %', ascending=False)
    
    st.markdown("#### 📊 Missing Values Overview")
    st.dataframe(missing_df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🗑️ Remove Missing Values")
        remove_option = st.radio(
            "Choose removal option:",
            ["Remove from all columns", "Remove from specific columns"],
            key="missing_remove_option"
        )
        
        cols_to_check = []  # Initialize
        if remove_option == "Remove from specific columns":
            cols_to_check = st.multiselect(
                "Select columns:",
                df.columns,
                key="missing_remove_cols"
            )
        
        if st.button("🗑️ Remove Rows", use_container_width=True):
            start_time = time.time()
            with st.spinner("Removing missing values..."):
                if remove_option == "Remove from all columns":
                    new_df = drop_missing_rows(df)
                    affected = list(df.columns[df.isna().any()])
                else:
                    if cols_to_check:
                        new_df = drop_missing_rows(df, cols_to_check)
                        affected = cols_to_check
                    else:
                        st.warning("Please select columns!")
                        return
                
                # Show preview before applying
                st.session_state["temp_df"] = new_df
                st.session_state["temp_affected"] = affected
                st.session_state["temp_op"] = "Remove Missing Rows"
                st.session_state["temp_params"] = {"option": remove_option, "columns": cols_to_check if cols_to_check else "all"}
                st.session_state["temp_duration"] = time.time() - start_time

        if "temp_df" in st.session_state and st.session_state.get("temp_op") == "Remove Missing Rows":
            render_preview_metrics(df, st.session_state["temp_df"], st.session_state["temp_affected"])
            if st.button("Confirm Removal ✅", type="primary"):
                add_transformation(
                    st.session_state["temp_op"],
                    st.session_state["temp_params"],
                    st.session_state["temp_affected"],
                    st.session_state["temp_df"],
                    duration=st.session_state.get("temp_duration")
                )
                del st.session_state["temp_df"]
                st.success("✅ Transformation applied!")
                st.rerun()
    
    with col2:
        st.markdown("#### 📝 Fill Missing Values")
        fill_col = st.selectbox("Select column:", df.columns, key="fill_col")
        
        col_type = df[fill_col].dtype
        if pd.api.types.is_numeric_dtype(col_type):
            methods = ["Constant", "Mean", "Median", "Mode"]
        elif pd.api.types.is_datetime64_any_dtype(col_type):
            methods = ["Constant", "Forward Fill", "Backward Fill"]
        else:
            methods = ["Constant", "Mode (Most Frequent)"]
            
        fill_method = st.selectbox(
            "Fill method:",
            methods,
            key="fill_method"
        )
        
        const_value = None
        if fill_method == "Constant":
            const_value = st.text_input("Enter constant value:", key="const_value")
        
        if st.button("✨ Fill Values", use_container_width=True):
            with st.spinner("Filling missing values..."):
                new_df = df.copy()
                
                try:
                    if fill_method == "Mean":
                        new_df = fill_numeric(new_df, fill_col, "mean")
                    elif fill_method == "Median":
                        new_df = fill_numeric(new_df, fill_col, "median")
                    elif fill_method == "Mode" or fill_method == "Mode (Most Frequent)":
                        new_df = fill_mode(new_df, fill_col)
                    elif fill_method == "Forward Fill":
                        new_df = fill_forward(new_df, fill_col)
                    elif fill_method == "Backward Fill":
                        new_df = fill_backward(new_df, fill_col)
                    elif fill_method == "Constant" and const_value:
                        new_df = fill_constant(new_df, fill_col, const_value)
                    
                    filled_count = df[fill_col].isna().sum() - new_df[fill_col].isna().sum()
                    
                    if filled_count > 0:
                        add_transformation(
                            f"Fill Missing - {fill_method}",
                            {"column": fill_col, "method": fill_method, "value": const_value if const_value else ""},
                            [fill_col],
                            new_df
                        )
                        
                        st.success(f"✅ Filled {filled_count} missing values in '{fill_col}'!")
                        st.rerun()
                    else:
                        st.info(f"ℹ️ No missing values found in '{fill_col}'!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Drop columns by threshold
    st.markdown("---")
    st.markdown("#### 🎚️ Drop Columns by Missing Threshold")
    
    threshold = st.slider(
        "Drop columns with missing % above:",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=5.0,
        key="threshold_slider"
    )
    
    if st.button("🗑️ Drop Columns", use_container_width=True):
        new_df, dropped_cols = drop_columns_by_threshold(df, threshold/100)
        
        if dropped_cols:
            add_transformation(
                "Drop Columns by Threshold",
                {"threshold": f"{threshold}%"},
                dropped_cols,
                new_df
            )
            st.success(f"✅ Dropped columns: {', '.join(dropped_cols)}")
            st.rerun()
        else:
            st.info("ℹ️ No columns exceed the threshold!")

def show_duplicates_tab(df):
    """🔄 Duplicate Handling"""
    st.markdown("### 🔄 Duplicate Detection & Removal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 Detect Duplicates")
        
        dup_type = st.radio(
            "Check for:",
            ["Full row duplicates", "Duplicates in specific columns"],
            key="dup_type"
        )
        
        dup_cols = []
        if dup_type == "Duplicates in specific columns":
            dup_cols = st.multiselect(
                "Select columns:",
                df.columns,
                key="dup_cols"
            )
        
        if st.button("🔍 Find Duplicates", use_container_width=True):
            if dup_type == "Full row duplicates":
                duplicates = detect_duplicates(df)
                dup_count = df.duplicated().sum()
            else:
                if dup_cols:
                    duplicates = detect_duplicates_subset(df, dup_cols)
                    dup_count = df.duplicated(subset=dup_cols).sum()
                else:
                    st.warning("Please select columns!")
                    return
            
            if dup_count > 0:
                st.warning(f"⚠️ Found {dup_count} duplicate rows!")
                st.dataframe(duplicates, use_container_width=True)
            else:
                st.success("✅ No duplicates found!")
    
    with col2:
        st.markdown("#### 🗑️ Remove Duplicates")
        
        remove_type = st.radio(
            "Keep which occurrence?",
            ["First", "Last"],
            key="remove_type"
        )
        
        if st.button("✨ Remove Duplicates", use_container_width=True):
            subset = dup_cols if dup_type == "Duplicates in specific columns" and dup_cols else None
            keep = "first" if remove_type == "First" else "last"
            
            new_df = remove_duplicates(df, subset=subset, keep=keep)
            
            rows_removed = len(df) - len(new_df)
            
            if rows_removed > 0:
                add_transformation(
                    "Remove Duplicates",
                    {"type": remove_type, "subset": subset if subset else "full"},
                    list(df.columns),
                    new_df
                )
                
                st.success(f"✅ Removed {rows_removed} duplicate rows!")
                st.rerun()
            else:
                st.info("ℹ️ No duplicates found!")

def show_categorical_tab(df):
    """🏷️ Categorical Data Tools"""
    st.markdown("### 🏷️ Categorical Data Transformation")
    
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not cat_cols:
        st.info("ℹ️ No categorical columns found!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✨ Text Cleaning")
        text_col = st.selectbox("Select column:", cat_cols, key="text_col")
        
        text_ops = st.multiselect(
            "Choose operations:",
            ["Strip Whitespace", "Lowercase", "Title Case"],
            key="text_ops"
        )
        
        if st.button("🧹 Clean Text", use_container_width=True) and text_ops:
            new_df = df.copy()
            
            for op in text_ops:
                if op == "Strip Whitespace":
                    new_df = strip_whitespace(new_df, text_col)
                elif op == "Lowercase":
                    new_df = to_lowercase(new_df, text_col)
                elif op == "Title Case":
                    new_df = to_titlecase(new_df, text_col)
            
            add_transformation(
                "Text Cleaning",
                {"column": text_col, "operations": text_ops},
                [text_col],
                new_df
            )
            
            st.success(f"✅ Applied {len(text_ops)} text operations to '{text_col}'!")
            st.rerun()
    
    with col2:
        st.markdown("#### 🗺️ Category Mapping")
        map_col = st.selectbox("Select column to map:", cat_cols, key="map_col")
        
        st.markdown("Create mapping (old -> new):")
        unique_vals = df[map_col].unique()[:5]  # Show first 5 unique values
        
        mapping = {}
        cols = st.columns(2)
        for i, val in enumerate(unique_vals):
            with cols[i % 2]:
                new_val = st.text_input(f"'{val}' →", value=str(val), key=f"map_{map_col}_{val}")
                if new_val != str(val):
                    mapping[val] = new_val
        
        if mapping and st.button("🔄 Apply Mapping", use_container_width=True):
            new_df = map_categories(df.copy(), map_col, mapping)
            
            add_transformation(
                "Category Mapping",
                {"column": map_col, "mapping": mapping},
                [map_col],
                new_df
            )
            
            st.success(f"✅ Applied mapping to {len(mapping)} categories!")
            st.rerun()
    
    # Rare categories
    st.markdown("---")
    st.markdown("#### 🎲 Group Rare Categories")
    
    rare_col = st.selectbox("Select column for rare grouping:", cat_cols, key="rare_col")
    
    freq = df[rare_col].value_counts(normalize=True)
    st.markdown(f"**Unique values:** {len(freq)}")
    
    threshold = st.slider(
        "Frequency threshold (%):",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.5,
        key="rare_threshold"
    )
    
    rare_cats = freq[freq < threshold/100].index.tolist()
    if rare_cats:
        st.info(f"ℹ️ {len(rare_cats)} categories will be grouped as 'Other'")
        
        if st.button("🎯 Group Rare Categories", use_container_width=True):
            new_df = group_rare_categories(df.copy(), rare_col, threshold/100)
            
            add_transformation(
                "Group Rare Categories",
                {"column": rare_col, "threshold": f"{threshold}%"},
                [rare_col],
                new_df
            )
            
            st.success(f"✅ Grouped {len(rare_cats)} rare categories into 'Other'!")
            st.rerun()
    
    # One-hot encoding
    st.markdown("---")
    st.markdown("#### 🔢 One-Hot Encoding")
    
    ohe_col = st.selectbox("Select column to encode:", cat_cols, key="ohe_col")
    
    if st.button("🎲 Apply One-Hot Encoding", use_container_width=True):
        new_df = one_hot_encode(df.copy(), ohe_col)
        
        add_transformation(
            "One-Hot Encoding",
            {"column": ohe_col},
            [ohe_col],
            new_df
        )
        
        st.success(f"✅ Applied one-hot encoding to '{ohe_col}'!")
        st.rerun()

def show_numeric_tab(df):
    """🔢 Numeric Data Tools"""
    st.markdown("### 🔢 Numeric Data Transformation")
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not num_cols:
        st.info("ℹ️ No numeric columns found!")
        return
    
    tab_out, tab_scale = st.tabs(["📊 Outliers", "📏 Scaling"])
    
    with tab_out:
        st.markdown("#### 🚨 Outlier Detection & Treatment")
        
        outlier_col = st.selectbox("Select numeric column:", num_cols, key="outlier_col")
        
        # Show basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean", f"{df[outlier_col].mean():.2f}")
        with col2:
            st.metric("Std Dev", f"{df[outlier_col].std():.2f}")
        with col3:
            st.metric("Unique", df[outlier_col].nunique())
        
        # Detect outliers
        outliers_iqr = detect_outliers_iqr(df, outlier_col)
        
        if len(outliers_iqr) > 0:
            st.warning(f"⚠️ Found {len(outliers_iqr)} outliers using IQR method!")
            
            action = st.radio(
                "Choose action:",
                ["Remove outliers", "Cap outliers", "Keep outliers"],
                key="outlier_action"
            )
            
            if st.button("🚀 Apply Outlier Treatment", use_container_width=True):
                new_df = df.copy()
                
                if action == "Remove outliers":
                    new_df = remove_outliers(new_df, outlier_col)
                    op_name = "Remove Outliers"
                elif action == "Cap outliers":
                    new_df = cap_outliers(new_df, outlier_col)
                    op_name = "Cap Outliers"
                else:
                    op_name = "Keep Outliers"
                
                st.session_state["temp_df"] = new_df
                st.session_state["temp_affected"] = [outlier_col]
                st.session_state["temp_op"] = op_name
                st.session_state["temp_params"] = {"column": outlier_col, "action": action}

            if "temp_df" in st.session_state and "Outliers" in st.session_state.get("temp_op", ""):
                render_preview_metrics(df, st.session_state["temp_df"], st.session_state["temp_affected"])
                if st.button("Confirm Treatment ✅", type="primary"):
                    add_transformation(
                        st.session_state["temp_op"],
                        st.session_state["temp_params"],
                        st.session_state["temp_affected"],
                        st.session_state["temp_df"]
                    )
                    del st.session_state["temp_df"]
                    st.session_state["global_success"] = "✅ Transformation applied!"
                    st.rerun()

        else:
            st.success("✅ No outliers detected!")
    
    with tab_scale:
        st.markdown("#### 📏 Feature Scaling")
        
        scale_cols = st.multiselect(
            "Select columns to scale:",
            num_cols,
            key="scale_cols"
        )
        
        scale_method = st.radio(
            "Scaling method:",
            ["Min-Max Normalization", "Z-Score Standardization"],
            key="scale_method"
        )
        
        if scale_cols and st.button("📊 Preview Scaling", use_container_width=True):
            new_df = df.copy()
            
            if scale_method == "Min-Max Normalization":
                new_df = minmax_scale(new_df, scale_cols)
                op_name = "Min-Max Scaling"
            else:
                new_df = zscore_scale(new_df, scale_cols)
                op_name = "Z-Score Scaling"
            
            st.session_state["temp_df"] = new_df
            st.session_state["temp_affected"] = scale_cols
            st.session_state["temp_op"] = op_name
            st.session_state["temp_params"] = {"columns": scale_cols, "method": scale_method}

        if "temp_df" in st.session_state and "Scaling" in st.session_state.get("temp_op", ""):
            render_preview_metrics(df, st.session_state["temp_df"], st.session_state["temp_affected"])
            if st.button("Confirm Scaling ✅", type="primary"):
                add_transformation(
                    st.session_state["temp_op"],
                    st.session_state["temp_params"],
                    st.session_state["temp_affected"],
                    st.session_state["temp_df"]
                )
                del st.session_state["temp_df"]
                st.success("✅ Transformation applied!")
                st.rerun()

def show_column_ops_tab(df):
    """📏 Column Operations"""
    st.markdown("### 📏 Column Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✏️ Rename Column")
        old_name = st.selectbox("Select column to rename:", df.columns, key="rename_col")
        new_name = st.text_input("New column name:", key="new_name")
        
        if st.button("🔄 Rename", use_container_width=True) and new_name and new_name != old_name:
            if new_name in df.columns:
                st.error(f"Cannot rename column to '{new_name}' because it already exists. Please choose a different name.")
            else:
                new_df = rename_column(df.copy(), old_name, new_name)
                
                add_transformation(
                    "Rename Column",
                    {"old": old_name, "new": new_name},
                    [old_name],
                    new_df
                )
                
                st.success(f"✅ Renamed '{old_name}' to '{new_name}'!")
                st.rerun()
    
    with col2:
        st.markdown("#### 🗑️ Drop Column")
        drop_col = st.selectbox("Select column to drop:", df.columns, key="drop_col")
        
        if st.button("❌ Drop Column", use_container_width=True):
            new_df = drop_column(df.copy(), drop_col)
            
            add_transformation(
                "Drop Column",
                {"column": drop_col},
                [drop_col],
                new_df
            )
            
            st.success(f"✅ Dropped column '{drop_col}'!")
            st.rerun()
    
    # Create formula column
    st.markdown("---")
    st.markdown("#### 🧮 Create Column with Formula")
    
    new_col_name = st.text_input("New column name:", value="new_column", key="new_formula_col")
    
    st.markdown("**Available columns:** " + ", ".join(df.columns[:10]) + 
                ("..." if len(df.columns) > 10 else ""))
    
    formula = st.text_input(
        "Enter formula (e.g., col1 + col2, log(col1), col1 / col2):",
        key="formula"
    )
    
    if st.button("✨ Create Column", use_container_width=True) and formula and new_col_name:
        try:
            # Create a safe environment for eval
            safe_dict = {col: df[col] for col in df.columns}
            safe_dict.update({'log': np.log, 'exp': np.exp, 'sqrt': np.sqrt})
            
            new_df = create_formula_column(df.copy(), new_col_name, formula)
            
            add_transformation(
                "Create Formula Column",
                {"name": new_col_name, "formula": formula},
                [new_col_name],
                new_df
            )
            
            st.success(f"✅ Created new column '{new_col_name}'!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error in formula: {str(e)}")
    
    # Binning
    st.markdown("---")
    st.markdown("#### 📊 Binning")
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if num_cols:
        bin_col = st.selectbox("Select column to bin:", num_cols, key="bin_col")
        
        bin_type = st.radio("Bin type:", ["Equal-width", "Quantile-based"], key="bin_type")
        
        n_bins = st.slider("Number of bins:", min_value=2, max_value=10, value=4, key="n_bins")
        
        if st.button("📦 Create Bins", use_container_width=True):
            new_df = df.copy()
            
            if bin_type == "Equal-width":
                new_df = equal_width_bins(new_df, bin_col, n_bins)
                op_name = "Equal-width Binning"
            else:
                new_df = quantile_bins(new_df, bin_col, n_bins)
                op_name = "Quantile Binning"
            
            add_transformation(
                op_name,
                {"column": bin_col, "bins": n_bins},
                [f"{bin_col}_bin"],
                new_df
            )
            
            st.success(f"✅ Created {n_bins} bins for '{bin_col}'!")
            st.rerun()
    else:
        st.info("ℹ️ No numeric columns available for binning!")

def show_validation_tab(df):
    """✅ Data Validation"""
    st.markdown("### ✅ Data Validation Rules")
    
    tab_range, tab_cat, tab_null = st.tabs(["📏 Range Checks", "🏷️ Category Checks", "🚫 Null Checks"])
    
    with tab_range:
        st.markdown("#### 📏 Numeric Range Validation")
        
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if num_cols:
            range_col = st.selectbox("Select column:", num_cols, key="range_col")
            
            col1, col2 = st.columns(2)
            with col1:
                min_val = st.number_input("Min value:", value=float(df[range_col].min()), key="min_val")
            with col2:
                max_val = st.number_input("Max value:", value=float(df[range_col].max()), key="max_val")
            
            if st.button("🔍 Check Range", use_container_width=True):
                violations = range_check(df, range_col, min_val, max_val)
                
                if len(violations) > 0:
                    st.warning(f"⚠️ Found {len(violations)} rows outside range!")
                    st.dataframe(violations, use_container_width=True)
                    
                    # Export option
                    csv = violations.to_csv(index=False)
                    st.download_button(
                        "📥 Export Violations",
                        csv,
                        f"range_violations_{range_col}.csv",
                        "text/csv"
                    )
                else:
                    st.success("✅ All values within range!")
        else:
            st.info("ℹ️ No numeric columns available!")
    
    with tab_cat:
        st.markdown("#### 🏷️ Category Validation")
        
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if cat_cols:
            cat_col = st.selectbox("Select column:", cat_cols, key="cat_col_val")
            
            unique_vals = df[cat_col].unique()
            st.markdown(f"**Unique values found:** {len(unique_vals)}")
            
            # Show sample of current values
            st.markdown("Sample values: " + ", ".join([str(x) for x in unique_vals[:5]]))
            
            allowed_input = st.text_area(
                "Enter allowed values (one per line):",
                key="allowed_vals"
            )
            
            if allowed_input and st.button("🔍 Check Categories", use_container_width=True):
                allowed = [x.strip() for x in allowed_input.split("\n") if x.strip()]
                
                if allowed:
                    violations = allowed_categories(df, cat_col, allowed)
                    
                    if len(violations) > 0:
                        st.warning(f"⚠️ Found {len(violations)} rows with disallowed categories!")
                        st.dataframe(violations, use_container_width=True)
                        
                        csv = violations.to_csv(index=False)
                        st.download_button(
                            "📥 Export Category Violations",
                            csv,
                            f"category_violations_{cat_col}.csv",
                            "text/csv"
                        )
                    else:
                        st.success("✅ All values are in allowed categories!")
        else:
            st.info("ℹ️ No categorical columns available!")
    
    with tab_null:
        st.markdown("#### 🚫 Non-Null Validation")
        
        null_col = st.selectbox("Select column to check:", df.columns, key="null_col")
        
        if st.button("🔍 Check Nulls", use_container_width=True):
            violations = non_null_violation(df, null_col)
            
            if len(violations) > 0:
                st.warning(f"⚠️ Found {len(violations)} rows with null values in '{null_col}'!")
                st.dataframe(violations, use_container_width=True)
                
                csv = violations.to_csv(index=False)
                st.download_button(
                    "📥 Export Null Violations",
                    csv,
                    f"null_violations_{null_col}.csv",
                    "text/csv"
                )
            else:
                st.success(f"✅ No null values in '{null_col}'!")

def show_datatype_tab(df):
    """📅 Datatype Conversion & Cleaning"""
    st.markdown("### 📅 Datatype Conversion & Cleaning")
    
    col_to_convert = st.selectbox("Select column to convert:", df.columns, key="dt_col")
    target_type = st.selectbox("Target Type:", ["Numeric (Clean)", "Datetime", "Categorical"], key="dt_type")
    
    if target_type == "Numeric (Clean)":
        st.info("💡 This will remove currency symbols, commas, and spaces, then convert to numeric.")
        if st.button("🔍 Preview Numeric Cleaning", use_container_width=True):
            new_df = df.copy()
            new_df = clean_numeric_strings(new_df, col_to_convert)
            new_df = convert_to_numeric(new_df, col_to_convert)
            
            st.session_state["temp_df"] = new_df
            st.session_state["temp_affected"] = [col_to_convert]
            st.session_state["temp_op"] = "Numeric Cleaning & Conversion"
            st.session_state["temp_params"] = {"column": col_to_convert}

    elif target_type == "Datetime":
        parse_mode = st.radio("Parsing Mode:", ["Auto-detect", "Manual Format"], key="dt_parse_mode")
        fmt = None
        if parse_mode == "Manual Format":
            fmt = st.text_input("Enter format (e.g., %Y-%m-%d):", key="dt_fmt")
        
        if st.button("🔍 Preview Datetime Parsing", use_container_width=True):
            new_df = df.copy()
            new_df = convert_to_datetime(new_df, col_to_convert, fmt)
            
            st.session_state["temp_df"] = new_df
            st.session_state["temp_affected"] = [col_to_convert]
            st.session_state["temp_op"] = "Datetime Conversion"
            st.session_state["temp_params"] = {"column": col_to_convert, "format": fmt if fmt else "auto"}

    elif target_type == "Categorical":
        if st.button("🔍 Preview Category Conversion", use_container_width=True):
            new_df = df.copy()
            new_df = convert_to_category(new_df, col_to_convert)
            
            st.session_state["temp_df"] = new_df
            st.session_state["temp_affected"] = [col_to_convert]
            st.session_state["temp_op"] = "Category Conversion"
            st.session_state["temp_params"] = {"column": col_to_convert}

    # Common preview and confirm logic
    if "temp_df" in st.session_state and "Conversion" in st.session_state.get("temp_op", ""):
        render_preview_metrics(df, st.session_state["temp_df"], st.session_state["temp_affected"])
        if st.button("Confirm Conversion ✅", type="primary", use_container_width=True):
            add_transformation(
                st.session_state["temp_op"],
                st.session_state["temp_params"],
                st.session_state["temp_affected"],
                st.session_state["temp_df"]
            )
            del st.session_state["temp_df"]
            st.success("✅ Datatype updated!")
            st.rerun()

def show_transformation_log():
    """📝 Display transformation log"""
    st.markdown("---")
    st.markdown("### 📝 Transformation Recipe Log")
    
    if st.session_state.get("recipe_log"):
        # Create a DataFrame for better display
        log_df = pd.DataFrame(st.session_state["recipe_log"])
        
        # Format for display
        display_log = log_df.copy()
        if 'parameters' in display_log.columns:
            display_log['parameters'] = display_log['parameters'].astype(str)
        
        st.dataframe(display_log, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("↩️ Undo Last", use_container_width=True):
                if undo_transformation():
                    st.success("✅ Undid last transformation!")
                    st.rerun()
                else:
                    st.warning("⚠️ No more steps to undo!")
        
        with col2:
            if st.button("🔄 Reset to Original", use_container_width=True):
                if reset_dataset():
                    st.success("✅ Reset to original dataset!")
                    st.rerun()
        
        with col3:
            if st.button("🧹 Clear Session", use_container_width=True):
                reset_session()
                st.success("✅ Session cleared!")
                st.rerun()
        
        # Export options
        st.markdown("#### 📤 Export Options")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            # Export CSV
            if st.session_state["df"] is not None:
                csv = st.session_state["df"].to_csv(index=False)
                st.download_button(
                    "📥 Export CSV",
                    csv,
                    f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        with col_exp2:
            # Export Excel
            try:
                if st.session_state["df"] is not None:
                    # Create a bytes buffer for Excel
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        st.session_state["df"].to_excel(writer, index=False)
                    
                    st.download_button(
                        "📥 Export Excel",
                        output.getvalue(),
                        f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.warning(f"⚠️ Excel export error: {str(e)}")
        
        with col_exp3:
            # Export recipe as JSON
            if st.session_state["recipe_log"]:
                recipe_json = json.dumps(st.session_state["recipe_log"], indent=2, default=str)
                st.download_button(
                    "📥 Export Recipe",
                    recipe_json,
                    f"transformation_recipe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json",
                    use_container_width=True
                )
    else:
        st.info("No transformations applied yet. Start cleaning your data!")

show_transformation_page()