import re
import pandas as pd
from core import transformations, numeric_tools, categorical_tools, column_ops

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
        if col in df.columns:
            return column_ops.drop_column(df.copy(), col), "Drop Column", {"column": col}, [col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    # 2. Remove Duplicates
    if "remove duplicates" in cmd or "drop duplicates" in cmd:
        return transformations.remove_duplicates(df.copy()), "Remove Duplicates", {"subset": "full"}, list(df.columns)

    # 3. Fill Missing
    fill_match = re.search(r"fill missing in (.+) with (mean|median|mode)", cmd)
    if fill_match:
        col = fill_match.group(1).strip()
        method = fill_match.group(2).strip()
        if col in df.columns:
            new_df = df.copy()
            if method == "mean":
                new_df = transformations.fill_numeric(new_df, col, "mean")
            elif method == "median":
                new_df = transformations.fill_numeric(new_df, col, "median")
            elif method == "mode":
                new_df = transformations.fill_mode(new_df, col)
            return new_df, f"Fill Missing ({method})", {"column": col, "method": method}, [col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    # 4. Clean Text (Strip, Lower)
    clean_match = re.search(r"clean text in (.+)", cmd)
    if clean_match:
        col = clean_match.group(1).strip()
        if col in df.columns:
            new_df = df.copy()
            new_df = categorical_tools.strip_whitespace(new_df, col)
            new_df = categorical_tools.to_lowercase(new_df, col)
            return new_df, "Clean Text", {"column": col, "ops": ["strip", "lower"]}, [col]
        else:
            raise ValueError(f"Column '{col}' not found.")

    raise ValueError("Command not recognized. Try 'drop column age' or 'remove duplicates'.")
