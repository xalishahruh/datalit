import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def apply_smart_rotation(ax, labels, rotation=45, threshold=10):
    """
    Apply rotation if labels are too long or too many.
    If rotation is -1 (Auto), it checks if any label length >= threshold.
    """
    if rotation == -1: # Auto
        # Clean labels to get string representation
        str_labels = [str(l) for l in labels if l is not None]
        max_len = max([len(l) for l in str_labels]) if str_labels else 0
        num_labels = len(str_labels)
        
        # Apply rotation if any label is long (>= threshold) OR if there are many labels
        if max_len >= threshold or num_labels > 5: # Lowered num_labels trigger too
            rotation = 45
        else:
            rotation = 0
            
    if rotation:
        # Use tick_params for simpler rotation and ensure alignment
        plt.setp(ax.get_xticklabels(), rotation=rotation, ha='right', rotation_mode='anchor')
    
    return rotation

def plot_histogram(df, column, bins=20):
    """Used for analyzing numeric distributions."""
    fig, ax = plt.subplots()
    ax.hist(df[column].dropna(), bins=bins)
    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column, labelpad=15)
    ax.set_ylabel("Frequency", labelpad=15)
    return fig

def plot_box(df, column, group=None, rotation=0):
    """
    Used for outlier detection and spread analysis.
    Assumption: Grouping by a categorical variable allows for side-by-side comparison of 
    numeric distributions across different segments (e.g., Sales by Region).
    If no group is provided, it visualizes the overall distribution of the column.
    """
    fig, ax = plt.subplots()
    if group:
        plot_df = df.copy()
        # Check if the group column is datetime-like
        if pd.api.types.is_datetime64_any_dtype(plot_df[group]):
            plot_df[group] = pd.to_datetime(plot_df[group]).dt.date
            
        sns.boxplot(data=plot_df, x=group, y=column, ax=ax)
        
        # Force a draw if needed to populate labels, though usually not req for sns
        labels = plot_df[group].unique()
        apply_smart_rotation(ax, labels, rotation=rotation)
    else:
        sns.boxplot(y=df[column], ax=ax)
        
    ax.set_title(f"Boxplot of {column}")
    plt.tight_layout()
    return fig

def plot_scatter(df, x, y, color=None):
    """
    Used for numeric relationships between two variables.
    
    Assumption: Color encoding (hue) is used to identify categorical patterns or clusters 
    within the scatter plot (e.g., Age vs Salary, colored by Department).
    This helps in understanding if relationships differ across categories.
    """
    fig, ax = plt.subplots()
    sns.scatterplot(data=df, x=x, y=y, hue=color, ax=ax)
    ax.set_title(f"{y} vs {x}")
    ax.set_xlabel(x, labelpad=15)
    ax.set_ylabel(y, labelpad=15)
    
    # Move legend outside the plot area to prevent overlapping with data points
    if color:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    plt.tight_layout()
    return fig

def plot_line(df, x, y, rotation=45, date_format=None):
    """Used for time-based trends."""
    fig, ax = plt.subplots()
    df_sorted = df.sort_values(x)
    
    # Apply date formatting if x is datetime
    if date_format and pd.api.types.is_datetime64_any_dtype(df_sorted[x]):
        from matplotlib.dates import DateFormatter
        ax.xaxis.set_major_formatter(DateFormatter(date_format))
        
    ax.plot(df_sorted[x], df_sorted[y])
    ax.set_title(f"{y} over {x}")
    ax.set_xlabel(x, labelpad=15)
    ax.set_ylabel(y, labelpad=15)
    
    # Apply smart rotation
    apply_smart_rotation(ax, df_sorted[x].tolist(), rotation=rotation)
        
    plt.tight_layout()
    return fig

def plot_grouped_bar(df, x, y, agg="mean", rotation=45):
    """Used for categorical comparisons."""
    grouped = df.groupby(x)[y].agg(agg).reset_index()
    fig, ax = plt.subplots()
    sns.barplot(data=grouped, x=x, y=y, ax=ax)
    ax.set_title(f"{agg} of {y} by {x}")
    ax.set_xlabel(x, labelpad=15)
    ax.set_ylabel(y, labelpad=15)
    
    # Apply smart rotation
    apply_smart_rotation(ax, grouped[x].tolist(), rotation=rotation)
        
    plt.tight_layout()
    return fig

def plot_correlation_heatmap(df):
    """Used for numeric relationships across many columns."""
    corr = df.select_dtypes(include="number").corr()
    if corr.empty:
        return None
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlation Matrix")
    return fig

def plot_area(df, x, y, rotation=45):
    """Used for cumulative time-based trends."""
    fig, ax = plt.subplots()
    df_sorted = df.sort_values(x)
    ax.fill_between(df_sorted[x], df_sorted[y], alpha=0.5)
    ax.plot(df_sorted[x], df_sorted[y])
    ax.set_title(f"Area Chart: {y} over {x}")
    ax.set_xlabel(x, labelpad=15)
    ax.set_ylabel(y, labelpad=15)
    apply_smart_rotation(ax, df_sorted[x].tolist(), rotation=rotation)
    plt.tight_layout()
    return fig

def plot_pie(df, x, y, agg="sum"):
    """Used for part-to-whole categorical breakdown."""
    grouped = df.groupby(x)[y].agg(agg).reset_index()
    fig, ax = plt.subplots()
    ax.pie(grouped[y], labels=grouped[x], autopct='%1.1f%%', startangle=140)
    ax.set_title(f"{agg.capitalize()} of {y} by {x}")
    plt.tight_layout()
    return fig
