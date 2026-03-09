import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_histogram(df, x_col, bins=20, title="Histogram"):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df[x_col], bins=bins, kde=True, ax=ax)
    ax.set_title(title)
    return fig

def create_boxplot(df, x_col, y_col=None, title="Box Plot"):
    fig, ax = plt.subplots(figsize=(10, 6))
    if y_col:
        sns.boxplot(data=df, x=x_col, y=y_col, ax=ax)
    else:
        sns.boxplot(data=df, y=x_col, ax=ax)
    ax.set_title(title)
    return fig

def create_scatter(df, x_col, y_col, color_col=None, title="Scatter Plot"):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x=x_col, y=y_col, hue=color_col, ax=ax)
    ax.set_title(title)
    return fig

def create_line(df, x_col, y_col, group_col=None, title="Line Chart"):
    fig, ax = plt.subplots(figsize=(10, 6))
    # Ensure x is sorted for line chart if it's numeric/datetime
    df_sorted = df.sort_values(by=x_col)
    sns.lineplot(data=df_sorted, x=x_col, y=y_col, hue=group_col, ax=ax)
    ax.set_title(title)
    return fig

def create_bar(df, x_col, y_col, agg_func="mean", group_col=None, title="Bar Chart"):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x=x_col, y=y_col, hue=group_col, estimator=agg_func, ax=ax)
    ax.set_title(title)
    return fig

def create_heatmap(df, title="Correlation Heatmap"):
    fig, ax = plt.subplots(figsize=(12, 10))
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    ax.set_title(title)
    return fig
