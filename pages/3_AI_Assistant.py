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
    if st.button("🔄 Reset Suggestions", use_container_width=True):
        st.session_state["dismissed_suggestions"] = []
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

# Suggestions Data
suggestions = suggestion_engine.analyze_dataset(df)
if "dismissed_suggestions" not in st.session_state:
    st.session_state["dismissed_suggestions"] = []

# Filter out dismissed ones
active_suggestions = [s for s in suggestions if s["id"] not in st.session_state["dismissed_suggestions"]]

with col2:
    st.metric("Active Suggestions", len(active_suggestions))

with col3:
    st.metric("Critical Issues", sum(1 for s in active_suggestions if s["severity"] == "critical"))

st.divider()

# --- Manual Insights Dashboard (Stats for each element) ---
st.subheader("📊 Manual Data Insights")
with st.expander("🔎 Explore Column-Level Statistics", expanded=False):
    cols = st.columns(4)
    for i, col_name in enumerate(df.columns):
        with cols[i % 4]:
            dtype = str(df[col_name].dtype)
            nulls = df[col_name].isna().sum()
            uniques = df[col_name].nunique()
            
            st.markdown(f"""
                <div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                    <h4 style="margin: 0; font-size: 0.9rem; color: #6c5ce7;">{col_name}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 0.8rem; opacity: 0.7;">Type: {dtype}</p>
                    <p style="margin: 2px 0 0 0; font-size: 0.8rem; opacity: 0.7;">Nulls: {nulls} | Uniques: {uniques}</p>
                </div>
            """, unsafe_allow_html=True)

def display_beautiful_insights(text):
    """Parses and renders AI insights using dashboard UI elements."""
    if not text:
        return
        
    parts = {}
    current_key = None
    
    for line in text.split('\n'):
        line = line.strip()
        if "[SUMMARY]" in line:
            current_key = "summary"
            parts[current_key] = []
        elif "[RISKS]" in line:
            current_key = "risks"
            parts[current_key] = []
        elif "[RECOMMENDATIONS]" in line:
            current_key = "recommendations"
            parts[current_key] = []
        elif current_key and line:
            parts[current_key].append(line)

    # 1. Summary Card
    if "summary" in parts:
        summary_text = " ".join(parts["summary"])
        st.markdown(f"""
            <div class="summary-card">
                <h3 style="margin:0; font-size: 1.2rem; color: #6c5ce7;">Executive Data Health Summary</h3>
                <p style="margin-top: 10px; font-size: 1.1rem; line-height: 1.6;">{summary_text}</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")

    # 2. Risks & Recommendations in Columns
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("### ⚠️ Critical Risks")
        if "risks" in parts:
            for risk in parts["risks"]:
                st.markdown(f"""<div class="insight-card">{risk}</div>""", unsafe_allow_html=True)
        else:
            st.info("No specific risks identified.")
            
    with col_r2:
        st.markdown("### 🎯 Strategic Actions")
        if "recommendations" in parts:
            for rec in parts["recommendations"]:
                st.markdown(f"""<div class="insight-card">{rec}</div>""", unsafe_allow_html=True)
        else:
            st.info("No specific recommendations.")

# --- Suggestion Feed ---
st.subheader("💡 Smart Suggestions")

if not active_suggestions:
    st.balloons()
    st.success("No issues found! Your dataset is ready for analysis.")
else:
    for s in active_suggestions:
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
                    st.session_state["dismissed_suggestions"].append(s["id"])
                    st.rerun()
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
        display_beautiful_insights(st.session_state["ai_insights"])
    else:
        st.info("Click the button to generate deep insights into your data's strategic quality and potential risks.")

# --- Empty State Footer ---
if len(df) == 0:
    st.error("The current dataset is empty. Check your filters or upload a valid file.")
