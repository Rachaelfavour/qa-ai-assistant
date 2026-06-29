import streamlit as st
import re
import json
import pandas as pd
import io
import datetime
import requests
import base64
from ai_helper import call_openai

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# SPLIT SECTIONS
sections = re.split(
    r"\n(?=[A-Z \-]+ -|===|[A-Z \-]+ SCENARIOS|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING|AUTHENTICATION & AUTHORIZATION|SESSION MANAGEMENT|DATA SECURITY|API SECURITY)",
    content
)

if "clear_clicked" not in st.session_state:
    st.session_state.clear_clicked = False

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# ✅ ✅ ✅ ADDITION 1 — MODE + WORKFLOW SWITCH
st.title("🤖 Agentic QA Automation Platform")
st.write("Automate your end-to-end QA workflow using specialised AI agents. Describe your feature once, and the QA Orchestrator coordinates multiple AI agents to analyse requirements, generate test cases, assess testing risk, create Azure DevOps test plans, and produce a complete QA report.")

col1, col2 = st.columns(2)

with col1:
    workflow_mode = st.radio(
        "Choose Workflow:",
        ["🚀 Run Full QA Workflow (Orchestrator)", "🔽 Use Individual Tools (Manual Control)"]
    )

with col2:
    app_mode = st.radio(
        "Mode:",
        ["🧪 Demo Mode (No Azure)", "🔴 Live Mode (Azure Enabled)"]
    )

if app_mode.startswith("🧪"):
    st.info("Demo Mode active: Azure actions are simulated ✅")

# ============================================
# EXISTING CODE CONTINUES (UNCHANGED)
# ============================================

def log_feedback(feature_name, rating, context=""):
    st.session_state.feedback_log.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "feature": feature_name,
        "rating": rating,
        "context": context[:100]
    })

def feedback_buttons(feature_name, context="", key_suffix=""):
    st.write("Was this helpful?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Yes", key=f"up_{key_suffix}"):
            log_feedback(feature_name, "up", context)
            st.success("Thanks for the feedback!")
    with col2:
        if st.button("👎 No", key=f"down_{key_suffix}"):
            log_feedback(feature_name, "down", context)
            st.info("Thanks — noted for improvement.")

def extract_json_array(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]
    text = re.sub(r":\s*N/A\s*,", ': "N/A",', text)
    text = re.sub(r":\s*N/A\s*}", ': "N/A"}', text)
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return json.loads(text)

def flatten_value(v):
    if isinstance(v, dict):
        return ", ".join(f"{k}: {val}" for k, val in v.items())
    if isinstance(v, list):
        return ", ".join(str(item) for item in v)
    return v

# ============================================
# AGENTIC QA ORCHESTRATOR
# ============================================
st.write("---")
st.write("## 🚀 QA Orchestrator")

agent_feature = st.text_area(
    "Describe the feature you want to test:",
    placeholder="e.g. User can book a car service appointment online",
    key="agent_input"
)

agent_plan_name = st.text_input(
    "Azure DevOps Test Plan Name:",
    placeholder="e.g. Car Booking Feature - Sprint 1"
)

# ✅ ✅ ✅ ADDITION 2 — ORCHESTRATOR MODE CONTROL
if workflow_mode.startswith("🚀") and st.button("🚀 Run QA Workflow"):

    if not agent_feature.strip():
        st.warning("Please describe a feature first.")
    elif not agent_plan_name.strip():
        st.warning("Please enter a test plan name.")
    else:
        agent_results = {}

        # AGENT 5 — DEMO MODE FIX ✅
        tc_json_output = call_openai(
            "You are a senior QA engineer...",
            f"Generate 10 structured test cases for: {agent_feature}"
        )

        try:
            tc_json_data = extract_json_array(tc_json_output)

            # ✅ ✅ ✅ ADDITION 3 — DEMO MODE
            if app_mode.startswith("🧪"):
                st.success("✅ Demo Mode: Test Plan simulated")
                agent_results["devops_success"] = True
                agent_results["epic_id"] = "DEMO-001"
                agent_results["created_tasks"] = [tc.get("test_scenario", "") for tc in tc_json_data[:3]]

            else:
                success, epic_url_view, epic_id, created_tasks = create_azure_devops_task_plan(agent_plan_name, tc_json_data)

        except Exception as e:
            st.error(e)

# ============================================
# ✅ ✅ ✅ ADDITION 4 — MANUAL MODE CONTROL
# ============================================
if workflow_mode.startswith("🔽"):
    st.write("---")
    with st.expander("🔧 Individual QA Tools"):
        st.write("Use these tools individually if you prefer manual control over each step.")

        st.write("### 📝 Requirement Gathering")
        rough_idea = st.text_area("Describe your rough idea:")
        if st.button("Generate Structured Requirement"):
            if rough_idea.strip():
                st.write(call_openai("Create requirement", rough_idea))
