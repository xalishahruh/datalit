import streamlit as st
import pandas as pd
import time
from services import dataset_manager, suggestion_engine
from core import ai_assistant, transformations

# Page Config
st.set_page_config(page_title="DataLit | AI Assistant", page_icon="🤖", layout="wide")

# Header
st.title("🤖 AI Assistant")
st.caption("Intelligent data cleaning recommendations and AI-driven insights for your dataset.")

# Check for Dataset
if not dataset_manager.dataset_exists():
    st.warning("No dataset loaded. Please go to the **Home** page to upload a CSV/Excel file.")
    st.stop()

# Load Data
df = dataset_manager.get_dataset()

# Sidebar Settings
with st.sidebar:
    st.header("AI Settings")
    enable_ai = st.toggle("Enable External AI Insights", value=False)
    api_key = st.text_input("OpenAI API Key (Optional)", type="password") if enable_ai else None
    
    if st.button("Clear Cache & Recalculate"):
        st.cache_data.clear()
        st.rerun()

# Layout: 2 Columns for Header metrics
col1, col2, col3 = st.columns([1, 1, 1])

# Health Score
health_score = suggestion_engine.calculate_health_score(df)
with col1:
    st.metric("Data Health Score", f"{health_score}/100")
    if health_score > 90:
        st.success("Your data looks excellent!")
    elif health_score > 70:
        st.info("Good data, some tweaks recommended.")
    else:
        st.warning("Action required: critical issues found.")

# Suggestions Count
suggestions = suggestion_engine.analyze_dataset(df)
with col2:
    st.metric("Total Suggestions", len(suggestions))

with col3:
    st.metric("Critical Issues", sum(1 for s in suggestions if s["severity"] == "critical"))

st.divider()

# --- Suggestion Feed ---
st.subheader("💡 Smart Suggestions")

if not suggestions:
    st.balloons()
    st.success("No issues found! Your dataset is ready for analysis.")
else:
    for s in suggestions:
        with st.container():
            # Severity color
            color = {"critical": "red", "warning": "orange", "info": "blue"}[s["severity"]]
            
            # Use styling for card effect
            st.markdown(f"""
                <div style="border: 2px solid {color}; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: {color};">{s['title']}</h3>
                    <p style="margin: 10px 0;">{s['description']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons
            btn_col1, btn_col2 = st.columns([1, 4])
            with btn_col1:
                if s["auto_fixable"]:
                    if st.button(f"Fix Now", key=f"fix_{s['id']}"):
                        # APPLY FIX
                        with st.spinner(f"Applying fix for {s['title']}..."):
                            start_time = time.time()
                            
                            new_df = df.copy()
                            action = s["fix_action"]
                            params = s["params"]
                            
                            if action == "drop_duplicates":
                                new_df = transformations.remove_duplicates(new_df)
                            elif action == "drop_column":
                                new_df = new_df.drop(columns=[params["column"]])
                            elif action == "fill_missing":
                                if params["method"] == "median":
                                    new_df = transformations.fill_numeric(new_df, params["column"], "median")
                                else:
                                    new_df = transformations.fill_mode(new_df, params["column"])
                                
                            duration = time.time() - start_time
                            dataset_manager.add_transformation(
                                op_name=s["title"],
                                params=s["params"],
                                affected_cols=[s["params"].get("column", "all")],
                                df_after=new_df,
                                duration=duration
                            )
                            st.success(f"Applied: {s['title']}")
                            time.sleep(1)
                            st.rerun()
                else:
                    st.info("Manual check required.")
            
            with btn_col2:
                if st.button("Dismiss", key=f"dismiss_{s['id']}"):
                    st.toast("Suggestion dismissed.")
        st.write("") # Spacer

st.divider()

# --- AI Insights Panel ---
st.subheader("🧠 Deep Insights (AI)")

if st.button("✨ Generate AI Insights"):
    with st.spinner("Analyzing dataset patterns..."):
        summary = ai_assistant.generate_dataset_summary(df)
        insights = ai_assistant.generate_ai_insights(summary, api_enabled=enable_ai, api_key=api_key)
        st.markdown(insights)

# --- Empty State Footer ---
if len(df) == 0:
    st.error("The current dataset is empty. Check your filters or upload a valid file.")
