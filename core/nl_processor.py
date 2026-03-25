import re
import pandas as pd
import json
import openai
from core import transformations, numeric_tools, categorical_tools, column_ops

def _get_real_col(df, col_query):
    for c in df.columns:
        if str(c).lower() == col_query.lower():
            return c
    return None

def parse_and_execute(df, command):
    """
    Simple heuristic parser for natural language commands.
    Supported:
    - 'drop column [name]'
    - 'remove duplicates'
    - 'fill missing in [column] with [mean|median|mode]'
    - 'clean text in [column]'
    """
    cmd = command.lower().strip()
    
    # 1. Drop Column
    drop_match = re.search(r"drop column (.+)", cmd)
    if drop_match:
        col = drop_match.group(1).strip()
        real_col = _get_real_col(df, col)
        if real_col:
            return column_ops.drop_column(df.copy(), real_col), "Drop Column", {"column": real_col}, [real_col]
        else:
            raise ValueError(f"Column '{col}' not found. Make sure to spell it correctly.")

    # 2. Remove Duplicates
    if "remove duplicates" in cmd or "drop duplicates" in cmd:
        return transformations.remove_duplicates(df.copy()), "Remove Duplicates", {"subset": "full"}, list(df.columns)

    # 3. Fill Missing
    fill_match = re.search(r"fill missing in (.+) with (mean|median|mode)", cmd)
    if fill_match:
        col = fill_match.group(1).strip()
        method = fill_match.group(2).strip()
        real_col = _get_real_col(df, col)
        if real_col:
            new_df = df.copy()
            if method == "mean":
                new_df = transformations.fill_numeric(new_df, real_col, "mean")
            elif method == "median":
                new_df = transformations.fill_numeric(new_df, real_col, "median")
            elif method == "mode":
                new_df = transformations.fill_mode(new_df, real_col)
            return new_df, f"Fill Missing ({method})", {"column": real_col, "method": method}, [real_col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    # 4. Clean Text (Strip, Lower)
    clean_match = re.search(r"clean text in (.+)", cmd)
    if clean_match:
        col = clean_match.group(1).strip()
        real_col = _get_real_col(df, col)
        if real_col:
            new_df = df.copy()
            new_df = categorical_tools.strip_whitespace(new_df, real_col)
            new_df = categorical_tools.to_lowercase(new_df, real_col)
            return new_df, "Clean Text", {"column": real_col, "ops": ["strip", "lower"]}, [real_col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    # 5. Rename Column
    rename_match = re.search(r"rename (?:column )?(.+) to (.+)", cmd)
    if rename_match:
        old_col = rename_match.group(1).strip()
        new_col = rename_match.group(2).strip()
        real_col = _get_real_col(df, old_col)
        if real_col:
            return column_ops.rename_column(df.copy(), real_col, new_col), "Rename Column", {"old": real_col, "new": new_col}, [real_col]
        else:
            raise ValueError(f"Column '{old_col}' not found.")

    # 6. Remove Outliers
    outlier_match = re.search(r"remove outliers (?:from |in )?(.+)", cmd)
    if outlier_match:
        col = outlier_match.group(1).strip()
        real_col = _get_real_col(df, col)
        if real_col:
            new_df = numeric_tools.remove_outliers(df.copy(), real_col)
            return new_df, "Remove Outliers", {"column": real_col}, [real_col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    # 7. One-Hot Encode Categorical
    encode_match = re.search(r"(?:one-hot encode|one hot encode|encode) (.+)", cmd)
    if encode_match:
        col = encode_match.group(1).strip()
        real_col = _get_real_col(df, col)
        if real_col:
            new_df = categorical_tools.one_hot_encode(df.copy(), real_col)
            return new_df, "One-Hot Encode", {"column": real_col}, [real_col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    # 8. Drop Missing Rows
    drop_null_match = re.search(r"drop missing (?:rows )?(?:from |in )?(.+)", cmd)
    if drop_null_match:
        col = drop_null_match.group(1).strip()
        real_col = _get_real_col(df, col)
        if real_col:
            new_df = transformations.drop_missing_rows(df.copy(), [real_col])
            return new_df, "Drop Missing Rows", {"columns": [real_col]}, [real_col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    raise ValueError("Command not recognized. Check the available commands in the expander.")

def parse_nl_to_json(df, command, api_key, model, base_url="https://api.groq.com/openai/v1"):
    schema = []
    for col in df.columns:
        schema.append(f"{col} ({df[col].dtype})")
    schema_str = ", ".join(schema)
    
    system_prompt = f"""
You are a data processing assistant. The user wants to clean a dataset with the following schema:
{schema_str}

Convert the user's natural language command into a structured JSON array of transformation steps.
Return ONLY valid JSON, with nothing else. Do not wrap it in markdown block quotes.

Expected format:
{{
  "steps": [
    {{
      "operation": "fill_missing",  // Supported: "remove_duplicates", "drop_column", "clean_text", "rename_column", "remove_outliers", "one_hot_encode", "drop_missing_rows"
      "column": "column_name", // if applicable
      "method": "median", // if applicable (e.g. mean, median, mode)
      "new_name": "new_col_name" // if applicable (e.g. rename_column)
    }}
  ]
}}
"""
    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": command}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise ValueError(f"AI parsing failed: {str(e)}")

def execute_nl_json(df, json_payload):
    steps = json_payload.get("steps", [])
    if not steps:
        raise ValueError("No valid steps parsed from the AI response.")
        
    new_df = df.copy()
    affected_cols_total = []
    descriptions = []
    
    for step in steps:
        op = step.get("operation")
        col = step.get("column")
        
        real_col = _get_real_col(new_df, col) if col else None
                
        if op == "drop_column" and real_col:
            new_df = column_ops.drop_column(new_df, real_col)
            affected_cols_total.append(real_col)
            descriptions.append(f"Drop Column: {real_col}")
            
        elif op == "remove_duplicates":
            new_df = transformations.remove_duplicates(new_df)
            affected_cols_total.extend(new_df.columns)
            descriptions.append("Remove Duplicates")
            
        elif op == "fill_missing" and real_col:
            method = step.get("method", "median")
            if method == "mean":
                new_df = transformations.fill_numeric(new_df, real_col, "mean")
            elif method == "median":
                new_df = transformations.fill_numeric(new_df, real_col, "median")
            elif method in ["mode", "most_frequent"]:
                new_df = transformations.fill_mode(new_df, real_col)
            affected_cols_total.append(real_col)
            descriptions.append(f"Fill Missing in {real_col} ({method})")
            
        elif op == "clean_text" and real_col:
            new_df = categorical_tools.strip_whitespace(new_df, real_col)
            new_df = categorical_tools.to_lowercase(new_df, real_col)
            affected_cols_total.append(real_col)
            descriptions.append(f"Clean Text in {real_col}")
            
        elif op == "rename_column" and real_col:
            new_name = step.get("new_name")
            if new_name:
                new_df = column_ops.rename_column(new_df, real_col, new_name)
                affected_cols_total.append(new_name)
                descriptions.append(f"Rename Column: {real_col} to {new_name}")
                
        elif op == "remove_outliers" and real_col:
            new_df = numeric_tools.remove_outliers(new_df, real_col)
            affected_cols_total.append(real_col)
            descriptions.append(f"Remove Outliers from {real_col}")
            
        elif op == "one_hot_encode" and real_col:
            new_df = categorical_tools.one_hot_encode(new_df, real_col)
            affected_cols_total.append(real_col)
            descriptions.append(f"One-Hot Encode {real_col}")
            
        elif op == "drop_missing_rows":
            if real_col:
                new_df = transformations.drop_missing_rows(new_df, [real_col])
                affected_cols_total.append(real_col)
                descriptions.append(f"Drop Missing Rows in {real_col}")
            else:
                new_df = transformations.drop_missing_rows(new_df)
                affected_cols_total.extend(new_df.columns)
                descriptions.append("Drop Missing Rows (All columns)")
        else:
            raise ValueError(f"Could not apply step '{op}' to column '{col}'. Please check your command.")
            
    # Remove duplicates from affected cols
    affected_cols_total = list(dict.fromkeys(affected_cols_total))
    final_op_name = " & ".join(descriptions)
    
    return new_df, final_op_name, {"steps": steps}, affected_cols_total
