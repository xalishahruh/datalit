import streamlit as st
import pandas as pd
import time
import streamlit.components.v1 as components
from services import dataset_manager, suggestion_engine
from core import ai_assistant, transformations, nl_processor

# Page Config
st.set_page_config(page_title="DataLit | AI Assistant", page_icon="🤖", layout="wide")

# Header
st.title("🤖 AI Assistant")
st.caption("Intelligent data cleaning recommendations and AI-driven insights for your dataset.")
st.warning("⚠️ **Disclaimer:** AI-generated insights and recommendations may be imperfect. Always verify the results before making critical decisions.")

# Check for Dataset
if not dataset_manager.dataset_exists():
    st.warning("No dataset loaded. Please go to the **Home** page to upload a CSV/Excel file.")
    st.stop()

# Load Data
df = dataset_manager.get_dataset()

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ AI Configuration")
    enable_ai = st.toggle("Enable External AI Insights", value=False, help="Connect to an LLM provider for deep dataset analysis and natural language processing.")
    
    if enable_ai:
        ai_provider = st.selectbox("AI Provider", ["Groq", "OpenAI"], index=0)
        
        if ai_provider == "Groq":
            if hasattr(st, "popover"):
                with st.popover("ℹ️ How to get a Groq API Key"):
                    st.markdown("""
                    **Free & Easy Setup:**
                    1. Go to [console.groq.com/keys](https://console.groq.com/keys)
                    2. Sign in with Google or GitHub
                    3. Navigate to **API Keys**
                    4. Click **Create API Key**
                    5. Copy the key (`gsk_...`) and paste it below!
                    """)
            else:
                with st.expander("ℹ️ How to get a Groq API Key"):
                    st.markdown("""
                    **Free & Easy Setup:**
                    1. Go to [console.groq.com/keys](https://console.groq.com/keys)
                    2. Sign in with Google or GitHub
                    3. Navigate to **API Keys**
                    4. Click **Create API Key**
                    5. Copy the key (`gsk_...`) and paste it below!
                    """)
            
            api_base_url = st.text_input("Base URL", value="https://api.groq.com/openai/v1")
            
            if "groq_api_key_val" not in st.session_state:
                st.session_state.groq_api_key_val = ""
                
            def set_default_groq():
                st.session_state.groq_api_key_val = "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"
                
            st.button("Load Default API Key", on_click=set_default_groq, type="secondary", use_container_width=True)
            api_key = st.text_input("Groq API Key", type="password", key="groq_api_key_val", placeholder="gsk-...")
            ai_model = st.selectbox("Preferred Model", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama3-8b-8192"], index=0)
        else:
            api_base_url = st.text_input("Base URL", value="https://api.openai.com/v1")
            
            if "oai_api_key_val" not in st.session_state:
                st.session_state.oai_api_key_val = ""
                
            api_key = st.text_input("OpenAI API Key", type="password", key="oai_api_key_val", placeholder="sk-...")
            ai_model = st.selectbox("Preferred Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    else:
        api_key = None
        ai_provider = "Groq"
        api_base_url = "https://api.groq.com/openai/v1"
        ai_model = "llama-3.3-70b-versatile"
    
    st.divider()
    if st.button("🔄 Reset Suggestions", use_container_width=True):
        st.session_state["dismissed_suggestions"] = []
        st.cache_data.clear()
        st.rerun()

is_ready = str(enable_ai and bool(api_key)).lower()
components.html(f"""
    <script>
    const doc = window.parent.document;
    let style = doc.getElementById('ai-blink-style');
    if (!style) {{
        style = doc.createElement('style');
        style.id = 'ai-blink-style';
        style.innerHTML = `
        @keyframes pulseGreen {{
            0% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }}
            50% {{ box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); background-color: rgba(40, 167, 69, 0.1) !important; color: #28a745 !important; border-color: #28a745 !important; }}
            100% {{ box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }}
        }}
        .blinking-ready {{
            animation: pulseGreen 2s infinite !important;
            border-color: #28a745 !important;
            color: #28a745 !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
        }}
        `;
        doc.head.appendChild(style);
    }}
    
    setTimeout(() => {{
        const isReady = {is_ready};
        const buttons = doc.querySelectorAll('.stButton button');
        buttons.forEach(btn => {{
            if (btn.innerText.includes('Generate Insights') || btn.innerText.includes('Generate Proposal')) {{
                if (isReady) {{
                    btn.classList.add('blinking-ready');
                }} else {{
                    btn.classList.remove('blinking-ready');
                }}
            }}
        }});
    }}, 200);
    </script>
""", height=0, width=0)

# Layout: 2 Columns for Header metrics
col1, col2, col3 = st.columns([1, 1, 1])

# Health Score
health_score = suggestion_engine.calculate_health_score(df)
# Health Score & Active Suggestions
suggestions = suggestion_engine.analyze_dataset(df)
if "dismissed_suggestions" not in st.session_state:
    st.session_state["dismissed_suggestions"] = []

# Filter out dismissed ones
active_suggestions = [s for s in suggestions if s["id"] not in st.session_state["dismissed_suggestions"]]
critical_count = sum(1 for s in active_suggestions if s["severity"] == "critical")
warning_count = sum(1 for s in active_suggestions if s["severity"] == "warning")

health_score = suggestion_engine.calculate_health_score(df)

with col1:
    st.metric("Data Health Score", f"{health_score}/100")
    if health_score > 90 and critical_count == 0:
        st.success("✨ Your data looks excellent!")
    elif health_score > 75 and critical_count == 0:
        st.info("ℹ️ Good data, minor improvements suggested.")
    elif critical_count > 0:
        st.error("⚠️ Urgent: Critical data quality issues detected!")
    else:
        st.warning("⚡ Priority: Multiple quality issues need attention.")

with col2:
    st.metric("Active Suggestions", len(active_suggestions))

with col3:
    st.metric("Critical Issues", critical_count)

st.divider()

# --- Manual Insights Dashboard (Stats for each element) ---
st.subheader("📊 Manual Data Insights")
st.caption("Click a column below to see deeper insights and statistics.")

if "selected_col" not in st.session_state:
    st.session_state["selected_col"] = None

# Grid Dashboard of pressable tiles
cols = st.columns(4)
for i, col_name in enumerate(df.columns):
    with cols[i % 4]:
        dtype = str(df[col_name].dtype)
        # Using button with a multi-line format
        if st.button(f"**{col_name}**\n\n{dtype}", key=f"btn_{col_name}", use_container_width=True, type="secondary"):
            st.session_state["selected_col"] = col_name

# Detailed Insight Pane
if st.session_state["selected_col"]:
    sel_col = st.session_state["selected_col"]
    with st.container():
        st.markdown(f"""
            <div style="background-color: rgba(108, 92, 231, 0.1); border: 1px solid #6c5ce7; padding: 25px; border-radius: 15px; margin-top: 20px; margin-bottom: 35px;">
                <h3 style="margin:0; color: #6c5ce7;">Detailed Insight: {sel_col}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        with detail_col1:
            st.write("**Core Statistics**")
            st.write(f"- Data type: `{df[sel_col].dtype}`")
            st.write(f"- Unique values: `{df[sel_col].nunique()}`")
            st.write(f"- Non-null count: `{df[sel_col].count()}`")
            st.write(f"- Missing values: `{df[sel_col].isna().sum()}`")
            
        with detail_col2:
            st.write("**Top Values**")
            top_v = df[sel_col].value_counts().head(5)
            st.dataframe(top_v, use_container_width=True)
            
        with detail_col3:
            if pd.api.types.is_numeric_dtype(df[sel_col]):
                st.write("**Numeric Profile**")
                st.write(f"- Mean: `{df[sel_col].mean():.2f}`")
                st.write(f"- Median: `{df[sel_col].median():.2f}`")
                st.write(f"- Outliers (IQR): `{len(df[(df[sel_col] < df[sel_col].quantile(0.25) - 1.5*(df[sel_col].quantile(0.75)-df[sel_col].quantile(0.25))) | (df[sel_col] > df[sel_col].quantile(0.75) + 1.5*(df[sel_col].quantile(0.75)-df[sel_col].quantile(0.25)))])}`")
            else:
                st.write("**Categorical Profile**")
                st.write(f"- Most frequent: `{df[sel_col].mode().iloc[0] if not df[sel_col].mode().empty else 'N/A'}`")
                st.write(f"- Least frequent: `{df[sel_col].value_counts().tail(1).index[0]}`")

        if st.button("Close Deep Insight"):
            st.session_state["selected_col"] = None
            st.rerun()

st.write("") # Spacer

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

# --- NEW: NL Command Interface ---
st.divider()
st.subheader("⌨️ Natural Language Commands (Beta)")
st.caption("Type commands to apply transformations instantly.")

with st.expander("📖 View Available Commands & Dataset Examples"):
    st.markdown("Here are the natural language commands you can execute right now. The examples below use your actual dataset's columns!")
    
    all_cols = list(df.columns)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.markdown("**1. Structure Operations**")
        st.code("remove duplicates")
        if all_cols:
            st.code(f"drop column {all_cols[-1]}")
            st.code(f"drop missing in {all_cols[0]}")
            if len(all_cols) >= 2:
                st.code(f"rename {all_cols[0]} to new_name")
            
    with col_ex2:
        st.markdown("**2. Cleaning Operations**")
        if num_cols:
            st.code(f"fill missing in {num_cols[0]} with median")
            st.code(f"remove outliers from {num_cols[-1]}")
        if cat_cols:
            st.code(f"clean text in {cat_cols[0]}")
            st.code(f"encode {cat_cols[-1]}")

if "pending_nl_transformation" not in st.session_state:
    st.session_state["pending_nl_transformation"] = None

with st.container():
    col_nl1, col_nl2 = st.columns([4, 1])
    with col_nl1:
        nl_cmd = st.text_input("Enter command:", placeholder=f"e.g., drop column {all_cols[-1] if all_cols else 'age'}", key="nl_input")
    with col_nl2:
        btn_label = "Generate Proposal ✨" if enable_ai else "Execute Command"
        if st.button(btn_label, type="primary", use_container_width=True) and nl_cmd:
            if enable_ai:
                with st.spinner("AI is analyzing your command..."):
                    try:
                        proposed_json = nl_processor.parse_nl_to_json(df, nl_cmd, api_key, ai_model, api_base_url)
                        if not proposed_json.get("steps"):
                            st.warning("AI could not extract any steps from your command.")
                        else:
                            st.session_state["pending_nl_transformation"] = {
                                "json": proposed_json,
                                "cmd": nl_cmd
                            }
                    except Exception as e:
                        st.error(f"❌ AI Parsing Error: {str(e)}")
            else:
                try:
                    new_df, op, params, aff_cols = nl_processor.parse_and_execute(df, nl_cmd)
                    dataset_manager.add_transformation(op, params, aff_cols, new_df)
                    st.success(f"✅ Executed: {op}")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")

if st.session_state["pending_nl_transformation"]:
    st.markdown("---")
    st.markdown("### 🤖 Review Proposed AI Transformation")
    pending_data = st.session_state["pending_nl_transformation"]
    
    st.json(pending_data["json"])
    
    col_app1, col_app2 = st.columns(2)
    with col_app1:
        if st.button("✅ Approve & Execute", use_container_width=True, type="primary"):
            try:
                with st.spinner("Applying AI transformations..."):
                    new_df, op, params, aff_cols = nl_processor.execute_nl_json(df, pending_data["json"])
                    dataset_manager.add_transformation(f"[AI] {op}", params, aff_cols, new_df)
                    st.success(f"✅ Executed: {op}")
                    st.session_state["pending_nl_transformation"] = None
                    time.sleep(0.5)
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error executing AI steps: {str(e)}")
    with col_app2:
        if st.button("❌ Reject & Clear", use_container_width=True):
            st.session_state["pending_nl_transformation"] = None
            st.rerun()

# --- NEW: Data Dictionary ---
st.divider()
st.subheader("📖 Automatic Data Dictionary")
if st.button("Generate Schema Overview", type="secondary"):
    with st.spinner("Compiling data schema..."):
        schema_data = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isna().sum()
            missing_pct = (missing / len(df)) * 100
            unique = df[col].nunique()
            
            # Simple description based on dtype
            desc = "Categorical / Text" if dtype == 'object' else "Numeric / Quantitative"
            if "datetime" in dtype: desc = "Temporal / Date"
            
            schema_data.append({
                "Column": col,
                "Type": dtype,
                "Missing %": f"{missing_pct:.1f}%",
                "Unique Values": unique,
                "Sample Value": str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "N/A",
                "Description": desc
            })
        
        st.dataframe(pd.DataFrame(schema_data), use_container_width=True, hide_index=True)

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
                model=ai_model,
                base_url=api_base_url
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
