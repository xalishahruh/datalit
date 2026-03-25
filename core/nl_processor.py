import re
import pandas as pd
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
