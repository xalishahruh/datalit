import pandas as pd
from core import transformations, column_ops, numeric_tools, categorical_tools

def apply_step(df, step):
    """
    Applies a single transformation step to a dataframe.
    Step format: {"operation": str, "parameters": dict}
    """
    op = step.get('operation', '').lower()
    params = step.get('parameters', {})
    new_df = df.copy()

    try:
        # 1. Missing Values
        if "missing" in op and "row" in op:
            cols = params.get('columns')
            if params.get('option') == "Remove from all columns" or cols == "all":
                return transformations.drop_missing_rows(new_df)
            return transformations.drop_missing_rows(new_df, cols)
        
        elif "fill missing" in op:
            method = str(params.get('method', '')).lower()
            col = params.get('column')
            if any(m in method for m in ['mean', 'median']):
                return transformations.fill_numeric(new_df, col, 'mean' if 'mean' in method else 'median')
            elif 'mode' in method:
                return transformations.fill_mode(new_df, col)
            elif 'constant' in method:
                return transformations.fill_constant(new_df, col, params.get('value'))
            elif 'forward' in method:
                return transformations.fill_forward(new_df, col)
            elif 'backward' in method:
                return transformations.fill_backward(new_df, col)
        
        # 2. Duplicates
        elif "duplicate" in op:
            subset = params.get('subset')
            keep = str(params.get('type', 'First')).lower()
            return transformations.remove_duplicates(new_df, subset=None if str(subset).lower() == 'full' else subset, keep=keep)
        
        # 3. Column Operations
        elif "rename" in op:
            return column_ops.rename_column(new_df, params.get('old'), params.get('new'))
        
        elif "drop column" in op:
            return column_ops.drop_column(new_df, params.get('column'))

        elif "threshold" in op:
            thresh = float(str(params.get('threshold', '50%')).replace('%', '')) / 100
            new_df, _ = transformations.drop_columns_by_threshold(new_df, thresh)
            return new_df
            
        # 4. Categorical
        elif "text cleaning" in op:
            col = params.get('column')
            ops = params.get('operations', [])
            for text_op in ops:
                if "strip" in text_op.lower():
                    new_df = categorical_tools.strip_whitespace(new_df, col)
                elif "lower" in text_op.lower():
                    new_df = categorical_tools.to_lowercase(new_df, col)
                elif "title" in text_op.lower():
                    new_df = categorical_tools.to_titlecase(new_df, col)
            return new_df

        elif "mapping" in op:
            return categorical_tools.map_categories(new_df, params.get('column'), params.get('mapping'), params.get('unmatched', 'keep'))

        elif "encoding" in op:
            return categorical_tools.one_hot_encode(new_df, params.get('column'))

        # 5. Numeric
        elif "outlier" in op:
            col = params.get('column')
            action = str(params.get('action', '')).lower()
            if "remove" in action or "remove" in op:
                return numeric_tools.remove_outliers(new_df, col)
            elif "cap" in action or "cap" in op:
                return numeric_tools.cap_outliers(new_df, col)
        
        elif "scaling" in op:
            cols = params.get('columns')
            method = str(params.get('method', '')).lower()
            if "min" in method:
                return numeric_tools.minmax_scale(new_df, cols)
            else:
                return numeric_tools.zscore_scale(new_df, cols)
        
        elif "formula" in op:
            return column_ops.create_formula_column(new_df, params.get('name'), params.get('formula'))
            
        elif "binning" in op or "bin" in op:
            col = params.get('column')
            bins = params.get('bins', 4)
            if "quantile" in op:
                return column_ops.quantile_bins(new_df, col, bins)
            else:
                return column_ops.equal_width_bins(new_df, col, bins)

        # 6. Datatypes & Cleaning
        elif "numeric cleaning" in op:
            col = params.get('column')
            new_df = transformations.clean_numeric_strings(new_df, col)
            return transformations.convert_to_numeric(new_df, col)
            
        elif "datetime conversion" in op:
            return transformations.convert_to_datetime(new_df, params.get('column'), params.get('format'))
            
        elif "category conversion" in op:
            return transformations.convert_to_category(new_df, params.get('column'))

        elif "rare categories" in op:
            thresh_str = str(params.get('threshold', '5%')).replace('%', '')
            return categorical_tools.group_rare_categories(new_df, params.get('column'), float(thresh_str)/100)

    except Exception as e:
        print(f"Error applying step {op}: {e}")
        return df

    return new_df

def apply_recipe(df, recipe):
    """Replays an entire sequence of steps on a dataframe."""
    processed_df = df.copy()
    for step in recipe:
        processed_df = apply_step(processed_df, step)
    return processed_df

def get_step_python_code(step):
    """Returns the string representation of a step for the script exporter."""
    op = step.get('operation', '').lower()
    params = step.get('parameters', {})
    
    code_lines = []
    
    # 1. Missing Values
    if "missing" in op and "row" in op:
        if params.get('option') == "Remove from all columns" or params.get('columns') == "all":
            code_lines.append("    df = transformations.drop_missing_rows(df)")
        else:
            code_lines.append(f"    df = transformations.drop_missing_rows(df, {params.get('columns')})")
    
    elif "fill missing" in op:
        method = str(params.get('method', '')).lower()
        col = params.get('column')
        if "mean" in method:
            code_lines.append(f"    df = transformations.fill_numeric(df, '{col}', 'mean')")
        elif "median" in method:
            code_lines.append(f"    df = transformations.fill_numeric(df, '{col}', 'median')")
        elif 'mode' in method:
            code_lines.append(f"    df = transformations.fill_mode(df, '{col}')")
        elif 'constant' in method:
            code_lines.append(f"    df = transformations.fill_constant(df, '{col}', '{params.get('value')}')")
        elif 'forward' in method:
            code_lines.append(f"    df = transformations.fill_forward(df, '{col}')")
        elif 'backward' in method:
            code_lines.append(f"    df = transformations.fill_backward(df, '{col}')")

    # 2. Duplicates
    elif "duplicate" in op:
        subset = params.get('subset')
        keep = str(params.get('type', 'First')).lower()
        subset_val = None if str(subset).lower() == 'full' else subset
        code_lines.append(f"    df = transformations.remove_duplicates(df, subset={subset_val}, keep='{keep}')")
    
    # 3. Column Operations
    elif "rename" in op:
        code_lines.append(f"    df = column_ops.rename_column(df, '{params.get('old')}', '{params.get('new')}')")
    
    elif "drop column" in op:
        code_lines.append(f"    df = column_ops.drop_column(df, '{params.get('column')}')")

    elif "threshold" in op:
        thresh = float(str(params.get('threshold', '50%')).replace('%', '')) / 100
        code_lines.append(f"    df, _ = transformations.drop_columns_by_threshold(df, {thresh})")
        
    # 4. Categorical
    elif "text cleaning" in op:
        col = params.get('column')
        for text_op in params.get('operations', []):
            t_op = text_op.lower()
            if "strip" in t_op:
                code_lines.append(f"    df = categorical_tools.strip_whitespace(df, '{col}')")
            elif "lower" in t_op:
                code_lines.append(f"    df = categorical_tools.to_lowercase(df, '{col}')")
            elif "title" in t_op:
                code_lines.append(f"    df = categorical_tools.to_titlecase(df, '{col}')")

    elif "mapping" in op:
        code_lines.append(f"    df = categorical_tools.map_categories(df, '{params.get('column')}', {params.get('mapping')}, unmatched='{params.get('unmatched', 'keep')}')")

    elif "encoding" in op:
        code_lines.append(f"    df = categorical_tools.one_hot_encode(df, '{params.get('column')}')")

    elif "rare categories" in op:
        thresh_str = str(params.get('threshold', '5%')).replace('%', '')
        code_lines.append(f"    df = categorical_tools.group_rare_categories(df, '{params.get('column')}', {float(thresh_str)/100})")

    # 5. Numeric
    elif "outlier" in op:
        col = params.get('column')
        action = str(params.get('action', '')).lower()
        if "remove" in action or "remove" in op:
            code_lines.append(f"    df = numeric_tools.remove_outliers(df, '{col}')")
        elif "cap" in action or "cap" in op:
            code_lines.append(f"    df = numeric_tools.cap_outliers(df, '{col}')")
            
    elif "scaling" in op:
        cols = params.get('columns')
        method = str(params.get('method', '')).lower()
        if "min" in method:
            code_lines.append(f"    df = numeric_tools.minmax_scale(df, {cols})")
        else:
            code_lines.append(f"    df = numeric_tools.zscore_scale(df, {cols})")
            
    elif "formula" in op:
        code_lines.append(f"    df = column_ops.create_formula_column(df, '{params.get('name')}', '{params.get('formula')}')")
        
    elif "binning" in op or "bin" in op:
        col = params.get('column')
        bins = params.get('bins', 4)
        if "quantile" in op:
            code_lines.append(f"    df = column_ops.quantile_bins(df, '{col}', {bins})")
        else:
            code_lines.append(f"    df = column_ops.equal_width_bins(df, '{col}', {bins})")

    # 6. Datatypes & Cleaning
    elif "numeric cleaning" in op:
        col = params.get('column')
        code_lines.append(f"    df = transformations.clean_numeric_strings(df, '{col}')")
        code_lines.append(f"    df = transformations.convert_to_numeric(df, '{col}')")
        
    elif "datetime conversion" in op:
        fmt = params.get('format')
        fmt_val = f"'{fmt}'" if fmt and fmt != "auto" else "None"
        code_lines.append(f"    df = transformations.convert_to_datetime(df, '{params.get('column')}', {fmt_val})")
        
    elif "category conversion" in op:
        code_lines.append(f"    df = transformations.convert_to_category(df, '{params.get('column')}')")
            
    return "\n".join(code_lines) if code_lines else f"    # TODO: Mapping for {op}"
