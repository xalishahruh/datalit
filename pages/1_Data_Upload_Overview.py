import streamlit as st
from core.loader import load_dataset
from core.state_manager import set_dataset
from core.profiling import get_missing_values, get_duplicates, get_summary_stats, get_inferred_dtypes

st.title("Data Upload & Overview")
st.write("Upload your dataset to begin.")

uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "json"])

if uploaded_file is not None:
    try:
        df = load_dataset(uploaded_file)
    except Exception as e:
        st.error(e)
        df = None
    
    if df is not None:
        set_dataset(df)
        st.success("File uploaded successfully!")
        st.write("Data Preview:", df.head())

        rows, cols = df.shape

        st.subheader("Dataset Overview")
        st.write(f"Rows: {rows}")
        st.write(f"Columns: {cols}")

        st.write("Column Names:")
        st.write(list(df.columns))

        st.subheader("Inferred Data Types")
        inferred_types = get_inferred_dtypes(df)
        st.dataframe(inferred_types)

        missing_table = get_missing_values(df)
        st.subheader("Missing Values")
        st.dataframe(missing_table)

        duplicates = get_duplicates(df)
        st.subheader("Duplicates")
        st.write(f"Number of duplicates: {duplicates}")

        num_sum, cat_sum = get_summary_stats(df)

        st.subheader("Numeric Summary")
        st.dataframe(num_sum)

        st.subheader("Categorical Summary")
        st.dataframe(cat_sum)
