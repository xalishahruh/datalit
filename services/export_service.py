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
