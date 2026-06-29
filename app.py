import streamlit as st
import re
import json
import pandas as pd
import io
import datetime
import requests
import base64
from ai_helper import call_openai

# ============================================
# LOAD DATA
# ============================================
with open("qa_data.txt", "r") as f:
    content = f.read()

sections = re.split(
    r"\n(?=[A-Z \-]+ -|===|[A-Z \-]+ SCENARIOS|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING|AUTHENTICATION & AUTHORIZATION|SESSION MANAGEMENT|DATA SECURITY|API SECURITY)",
    content
)

# ============================================
# APP TITLE
# ============================================
st.title("🤖 Agentic QA Automation Platform")

st.write("""
Automate your end-to-end QA workflow using specialised AI agents.
Describe your feature once, and the QA Orchestrator coordinates multiple AI agents.
""")

# ============================================
# MODE SELECTION ✅ NEW
# ============================================
col1, col2 = st.columns(2)

with col1:
    workflow_mode = st.radio(
        "Choose Workflow Mode:",
        ["🚀 Run Full QA Workflow (Orchestrator)", "🔽 Use Individual Tools (Manual Control)"]
    )

with col2:
    app_mode = st.radio(
        "Mode:",
        ["🧪 Demo Mode (No Azure)", "🔴 Live Mode (Azure Enabled)"]
    )

if app_mode.startswith("🧪"):
    st.info("Demo Mode: Azure actions are simulated ✅")

st.markdown("---")

# ============================================
# HELPER FUNCTIONS
# ============================================
def extract_json_array(raw_text):
    text = raw_text.strip()
    text = re.sub(r"^```(json)?", "", text).replace("```", "")
    start = text.find("[")
    end = text.rfind("]")
    return json.loads(text[start:end+1])

# ============================================
# AZURE FUNCTIONS
# ============================================
def create_azure_devops_task_plan(plan_title, test_cases_json):
    try:
        pat = st.secrets.get("AZURE_DEVOPS_PAT")
        if not pat:
            return False, "No PAT", None, []

        org = "richkome"
        project = "QA-Assistant"

        credentials = base64.b64encode(f":{pat}".encode()).decode()
        headers = {"Content-Type": "application/json-patch+json", "Authorization": f"Basic {credentials}"}

        epic_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Epic?api-version=7.1"

        body = [
            {"op": "add", "path": "/fields/System.Title", "value": plan_title}
        ]

        res = requests.post(epic_url, headers=headers, json=body)
        epic_id = res.json().get("id")

        created_tasks = []
        for tc in test_cases_json[:5]:
            created_tasks.append(tc.get("test_scenario", ""))

        return True, f"Epic {epic_id} Created", epic_id, created_tasks

    except Exception as e:
        return False, str(e), None, []

# ============================================
# ORCHESTRATOR
# ============================================
if workflow_mode.startswith("🚀"):

    st.write("## 🚀 QA Orchestrator")

    feature = st.text_area("Describe feature:")
    plan = st.text_input("Test Plan Name:")

    if st.button("🚀 Run QA Workflow"):

        # 1. Requirement
        req = call_openai(
            "Create structured requirement",
            f"{feature}"
        )

        st.subheader("📋 Requirement")
        st.write(req)

        # 2. Test Cases
        tc = call_openai(
            "Generate test cases",
            f"{feature}"
        )

        st.subheader("🧪 Test Cases")
        st.code(tc)

        # 3. Risk
        risk = call_openai(
            "Generate risks",
            f"{feature}"
        )

        st.subheader("⚠️ Risks")
        st.write(risk)

        # 4. Azure
        st.subheader("🚀 Azure DevOps")

        tc_json = call_openai(
            "Return JSON test cases",
            feature
        )

        try:
            data = extract_json_array(tc_json)

            if app_mode.startswith("🧪"):
                st.success("✅ Demo Mode: Test Plan simulated")
            else:
                success, msg, _, tasks = create_azure_devops_task_plan(plan, data)

                if success:
                    st.success(msg)
                else:
                    st.error(msg)

        except:
            st.warning("Could not process Azure step")

# ============================================
# KNOWLEDGE BASE
# ============================================
st.write("---")
st.write("## 📚 QA Knowledge Base")

query = st.text_input("Search:")
if query:
    results = []
    for s in sections:
        if query.lower() in s.lower():
            results.append(s)

    for r in results[:5]:
        st.code(r)

# ============================================
# MANUAL TOOLS
# ============================================
if workflow_mode.startswith("🔽"):

    st.write("---")
    with st.expander("🔧 Manual QA Tools"):

        st.subheader("📝 Requirement Generator")

        txt = st.text_area("Enter idea")

        if st.button("Generate Requirement"):
            out = call_openai("Create requirement", txt)
            st.write(out)

        st.subheader("🧪 Test Case Generator")

        txt2 = st.text_area("Feature")

        if st.button("Generate Test Cases"):
            out2 = call_openai("Generate cases", txt2)
            st.code(out2)
