import streamlit as st
import pandas as pd
from core.state_manager import add_transformation, undo_last_transformation, reset_to_original
from core.transformations import (
    handle_missing, handle_duplicates, convert_types, 
    categorical_transform, handle_outliers, scale_data, column_operations
)
from utils.ui_utils import apply_custom_styles

st.set_page_config(page_title="Cleaning & Transformations", layout="wide")
apply_custom_styles()

st.title("🛠️ Data Cleaning & Transformations")

if st.session_state.working_df is None:
    st.warning("Please upload a dataset first!")
    st.stop()

df = st.session_state.working_df

# Sidebar Actions
with st.sidebar:
    st.header("Actions")
    if st.button("↩️ Undo Last Step", use_container_width=True):
        if undo_last_transformation():
            st.success("Last transformation undone.")
            st.rerun()
        else:
            st.warning("No transformations to undo.")
            
    if st.button("🔄 Reset to Original", use_container_width=True):
        if reset_to_original():
            st.success("Reset to original dataset.")
            st.rerun()

# 1. Missing Values
with st.expander("🩹 Handle Missing Values"):
    cols_with_missing = df.columns[df.isnull().any()].tolist()
    if not cols_with_missing:
        st.success("No missing values detected!")
    else:
        col_to_fix = st.selectbox("Select Column", cols_with_missing)
        missing_count = df[col_to_fix].isnull().sum()
        st.write(f"Column '{col_to_fix}' has {missing_count} missing values ({ (missing_count/len(df))*100:.2f}%).")
        
        strategy = st.selectbox("Imputation Strategy", 
                                ["Drop Rows", "Drop Column", "Constant", "Mean", "Median", "Mode", "Forward Fill", "Backward Fill"])
        
        fill_val = None
        if strategy == "Constant":
            fill_val = st.text_input("Value to fill")
        
        if st.button("Apply Imputation", key="apply_missing"):
            new_df = handle_missing(df, col_to_fix, strategy, fill_val)
            add_transformation("Missing Value Imputation", {"column": col_to_fix, "strategy": strategy, "value": fill_val}, [col_to_fix], new_df)
            st.success(f"Applied {strategy} to {col_to_fix}")
            st.rerun()

# 2. Duplicates
with st.expander("👯 Handle Duplicates"):
    total_dupes = df.duplicated().sum()
    st.write(f"Total full-row duplicates: {total_dupes}")
    
    dup_cols = st.multiselect("Select subset of columns for duplicate detection (optional)", df.columns.tolist())
    keep_opt = st.radio("Keep which occurrence?", ["first", "last"])
    
    if st.button("Remove Duplicates"):
        new_df = handle_duplicates(df, subset=dup_cols if dup_cols else None, keep=keep_opt)
        removed_count = len(df) - len(new_df)
        add_transformation("Remove Duplicates", {"subset": dup_cols, "keep": keep_opt}, dup_cols if dup_cols else "All", new_df)
        st.success(f"Removed {removed_count} duplicate rows.")
        st.rerun()

    if st.checkbox("Show Duplicate Groups"):
        dupes_only = df[df.duplicated(subset=dup_cols if dup_cols else None, keep=False)]
        if not dupes_only.empty:
            st.write("Repeating rows:")
            st.dataframe(dupes_only.sort_values(by=dup_cols if dup_cols else df.columns[0]), use_container_width=True)
        else:
            st.info("No duplicates found with the current selection.")

# 3. Data Types
with st.expander("🧬 Convert Data Types"):
    col_type = st.selectbox("Select Column to Convert", df.columns.tolist())
    st.write(f"Current type: {df[col_type].dtype}")
    
    target_type = st.selectbox("Convert to", ["Numeric", "Categorical", "Datetime"])
    
    dt_format = None
    if target_type == "Datetime":
        dt_format = st.text_input("Manual Format (optional, e.g. %Y-%m-%d)", placeholder="Auto-detect if empty")
        
    if st.button("Convert Type"):
        try:
            new_df = convert_types(df, col_type, target_type, dt_format)
            add_transformation("Type Conversion", {"column": col_type, "to": target_type, "format": dt_format}, [col_type], new_df)
            st.success(f"Converted {col_type} to {target_type}")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# 4. Outliers
with st.expander("📈 Handle Outliers"):
    num_cols = df.select_dtypes(include=[pd.np.number]).columns.tolist() if hasattr(pd, 'np') else df.select_dtypes(include=['number']).columns.tolist()
    if not num_cols:
        st.info("No numeric columns available.")
    else:
        out_col = st.selectbox("Select Numeric Column", num_cols)
        method = st.selectbox("Detection Method", ["IQR", "Z-Score"])
        threshold = st.slider("Threshold (standard is 1.5 for IQR, 3 for Z-Score)", 1.0, 5.0, 1.5 if method == "IQR" else 3.0)
        action = st.selectbox("Action", ["Remove", "Cap"])
        
        if st.button("Handle Outliers"):
            new_df = handle_outliers(df, out_col, method, action, threshold)
            impact = len(df) - len(new_df) if action == "Remove" else "Values adjusted"
            add_transformation("Outlier Handling", {"column": out_col, "method": method, "action": action, "threshold": threshold}, [out_col], new_df)
            st.success(f"Outliers handled for {out_col}. Impact: {impact}")
            st.rerun()

# 5. Categorical Transformations
with st.expander("🔡 Categorical Transformations"):
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if not cat_cols:
        st.info("No categorical/text columns available.")
    else:
        cat_col = st.selectbox("Select Column", cat_cols, key="cat_sel")
        cat_task = st.selectbox("Transformation", ["Whitespace", "Lowercase", "Title Case", "Group Rare"])
        
        task_params = {}
        if cat_task == "Group Rare":
            task_params['threshold'] = st.slider("Frequency Threshold (%)", 0.0, 50.0, 5.0) / 100.0
            
        if st.button("Apply Transformation", key="apply_cat"):
            new_df = categorical_transform(df, cat_col, cat_task, threshold=task_params.get('threshold'))
            add_transformation("Categorical Transform", {"column": cat_col, "task": cat_task, **task_params}, [cat_col], new_df)
            st.success(f"Applied {cat_task} to {cat_col}")
            st.rerun()

# 6. Scaling & Normalization
with st.expander("⚖️ Scaling & Normalization"):
    sc_num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if not sc_num_cols:
        st.info("No numeric columns available.")
    else:
        cols_to_scale = st.multiselect("Select Columns to Scale", sc_num_cols)
        sc_method = st.selectbox("Method", ["Min-Max", "Standard (Z-Score)"])
        
        if st.button("Apply Scaling"):
            if not cols_to_scale:
                st.warning("Please select at least one column.")
            else:
                new_df = scale_data(df, cols_to_scale, sc_method)
                add_transformation("Scaling", {"columns": cols_to_scale, "method": sc_method}, cols_to_scale, new_df)
                st.success(f"Applied {sc_method} scaling.")
                st.rerun()

# 7. Column Operations
with st.expander("📑 Column Operations"):
    col_op = st.selectbox("Select Operation", ["Rename", "Remove", "Math Formula", "Binning"])
    
    if col_op == "Rename":
        old_n = st.selectbox("Column to Rename", df.columns.tolist())
        new_n = st.text_input("New Name")
        if st.button("Rename Column"):
            new_df = column_operations(df, "Rename", {"old_name": old_n, "new_name": new_n})
            add_transformation("Rename Column", {"old": old_n, "new": new_n}, [old_n], new_df)
            st.rerun()
            
    elif col_op == "Remove":
        to_rem = st.multiselect("Columns to Remove", df.columns.tolist())
        if st.button("Remove Columns"):
            new_df = column_operations(df, "Remove", {"columns": to_rem})
            add_transformation("Remove Columns", {"columns": to_rem}, to_rem, new_df)
            st.rerun()

    elif col_op == "Math Formula":
        st.info("Example: col3 = col1 + col2 or log_col = log(col1)")
        new_c = st.text_input("New Column Name")
        formula = st.text_input("Formula (Pandas eval syntax)")
        if st.button("Create Column"):
            try:
                new_df = column_operations(df, "Math Formula", {"new_col": new_c, "formula": formula})
                add_transformation("Math Formula", {"new_col": new_c, "formula": formula}, [new_c], new_df)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    elif col_op == "Binning":
        bin_col = st.selectbox("Select Column to Bin", df.select_dtypes(include=['number']).columns.tolist())
        bin_new = st.text_input("New Binned Column Name", value=f"{bin_col}_bins")
        bin_method = st.selectbox("Binning Method", ["Equal Width", "Quantile"])
        bin_count = st.number_input("Number of Bins", min_value=2, max_value=20, value=5)
        if st.button("Apply Binning"):
            new_df = column_operations(df, "Binning", {"col": bin_col, "new_col": bin_new, "method": bin_method, "bins": bin_count})
            add_transformation("Binning", {"col": bin_col, "new_col": bin_new, "method": bin_method, "bins": bin_count}, [bin_new], new_df)
            st.rerun()

# 8. Data Validation
with st.expander("✅ Data Validation"):
    val_col = st.selectbox("Select Column to Validate", df.columns.tolist())
    val_type = st.selectbox("Rule Type", ["Numeric Range", "Allowed Categories", "Non-Null"])
    
    violation_df = pd.DataFrame()
    
    if val_type == "Numeric Range":
        min_v = st.number_input("Minimum Value", value=float(df[val_col].min()) if pd.api.types.is_numeric_dtype(df[val_col]) else 0.0)
        max_v = st.number_input("Maximum Value", value=float(df[val_col].max()) if pd.api.types.is_numeric_dtype(df[val_col]) else 100.0)
        if st.button("Check Violations"):
            violation_df = df[(df[val_col] < min_v) | (df[val_col] > max_v)]
            
    elif val_type == "Allowed Categories":
        allowed = st.text_input("Allowed Values (comma separated)")
        if st.button("Check Violations"):
            allowed_list = [x.strip() for x in allowed.split(",")]
            violation_df = df[~df[val_col].astype(str).isin(allowed_list)]
            
    elif val_type == "Non-Null":
        if st.button("Check Violations"):
            violation_df = df[df[val_col].isnull()]
            
    if not violation_df.empty:
        st.warning(f"Found {len(violation_df)} violations!")
        st.dataframe(violation_df, use_container_width=True)
        csv_viol = violation_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Violations CSV", csv_viol, "violations.csv", "text/csv")
    elif st.button("Check Violations", key="check_empty"):
        st.success("No violations found!")

# Current Data Preview
st.divider()
st.subheader("Current Data Preview")
st.dataframe(df.head(20), use_container_width=True)
st.write(f"Current Shape: {df.shape}")
