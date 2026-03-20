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
    st.header("⚙️ AI Configuration")
    enable_ai = st.toggle("Enable External AI Insights", value=False, help="Connect to OpenAI for deep dataset analysis")
    
    if enable_ai:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        ai_model = st.selectbox("Preferred Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    else:
        api_key = None
        ai_model = "gpt-4o-mini"
    
    st.divider()
    if st.button("🔄 Recalculate Suggestions", use_container_width=True):
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
            # Severity border color
            color = {"critical": "#ff4b4b", "warning": "#ffa500", "info": "#6c5ce7"}[s["severity"]]
            
            # Use styling for card effect
            st.markdown(f"""
                <div style="border-left: 5px solid {color}; background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: {color}; text-transform: uppercase; font-size: 0.8rem;">{s['severity']}</h4>
                    <h3 style="margin: 5px 0;">{s['title']}</h3>
                    <p style="margin: 10px 0; opacity: 0.9;">{s['description']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons
            btn_col1, btn_col2, _ = st.columns([1, 1, 3])
            with btn_col1:
                if s["auto_fixable"]:
                    if st.button(f"Fix Now", key=f"fix_{s['id']}", type="primary"):
                        with st.spinner(f"Applying fix..."):
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
                            st.toast(f"✅ Applied: {s['title']}")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    st.button("Manual", key=f"man_{s['id']}", disabled=True)
            
            with btn_col2:
                if st.button("Dismiss", key=f"dismiss_{s['id']}"):
                    st.toast("Suggestion hidden from view.")
        st.write("") # Spacer

st.divider()

# --- AI Insights Panel ---
st.subheader("🧠 Deep Strategy & Risk Analysis")

# Use session state to persist insights
if "ai_insights" not in st.session_state:
    st.session_state["ai_insights"] = None

col_in1, col_in2 = st.columns([1, 4])
with col_in1:
    if st.button("✨ Generate Insights", type="secondary", use_container_width=True):
        with st.spinner("Executing detailed AI analysis..."):
            summary = ai_assistant.generate_dataset_summary(df)
            st.session_state["ai_insights"] = ai_assistant.generate_ai_insights(
                summary, 
                api_enabled=enable_ai, 
                api_key=api_key,
                model=ai_model
            )
    
    if st.session_state["ai_insights"]:
        if st.button("🗑️ Clear Insights", use_container_width=True):
            st.session_state["ai_insights"] = None
            st.rerun()

with col_in2:
    if st.session_state["ai_insights"]:
        st.markdown(st.session_state["ai_insights"])
    else:
        st.info("Click the button to generate deep insights into your data's strategic quality and potential risks.")

# --- Empty State Footer ---
if len(df) == 0:
    st.error("The current dataset is empty. Check your filters or upload a valid file.")
