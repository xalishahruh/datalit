import streamlit as st
from core.state_manager import init_state
from utils.ui_utils import apply_custom_styles

def main():
    st.set_page_config(
        page_title="DataLit - Data Prep Studio",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    init_state()
    apply_custom_styles()

    st.title("DataLit - Data Prep Studio")
    st.markdown("""
    Welcome to **DataLit**, your all-in-one studio for data cleaning, preparation, and visualization.
    
    ### Getting Started
    1.  **Upload** your data in the **Upload & Overview** tab.
    2.  **Clean** and transform your dataset in **Data Cleaning**.
    3.  **Visualize** insights in the **Visualization Builder**.
    4.  **Export** your results and transformation report.
    """)

    if st.session_state.working_df is not None:
        st.info(f"Currently working with a dataset of {st.session_state.working_df.shape[0]} rows and {st.session_state.working_df.shape[1]} columns.")
    else:
        st.warning("No data loaded. Please go to the 'Upload & Overview' page to start.")

if __name__ == "__main__":
    main()
