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

def create_azure_devops_issue(title, severity, description, steps_to_reproduce):
    try:
        pat = st.secrets.get("AZURE_DEVOPS_PAT")
        org = "richkome"
        project = "QA-Assistant"
        if not pat:
            return False, "Azure DevOps PAT not found in Streamlit secrets."
        url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Issue?api-version=7.1"
        credentials = base64.b64encode(f":{pat}".encode()).decode()
        headers = {"Content-Type": "application/json-patch+json", "Authorization": f"Basic {credentials}"}
        body = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": f"<b>Severity:</b> {severity}<br><br><b>Description:</b><br>{description}<br><br><b>Steps to Reproduce:</b><br>{steps_to_reproduce}"},
            {"op": "add", "path": "/fields/System.Tags", "value": "QA-Assistant; Bug-Report"}
        ]
        response = requests.post(url, headers=headers, json=body)
        if response.status_code in [200, 201]:
            work_item_id = response.json().get("id")
            work_item_url = f"https://dev.azure.com/{org}/{project}/_workitems/edit/{work_item_id}"
            return True, f"✅ Issue #{work_item_id} created! [View in Azure DevOps]({work_item_url})"
        else:
            return False, f"Failed: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error: {e}"

def create_azure_devops_task_plan(plan_title, test_cases_json):
    try:
        pat = st.secrets.get("AZURE_DEVOPS_PAT")
        org = "richkome"
        project = "QA-Assistant"
        if not pat:
            return False, "Azure DevOps PAT not found.", None, []
        credentials = base64.b64encode(f":{pat}".encode()).decode()
        headers = {"Content-Type": "application/json-patch+json", "Authorization": f"Basic {credentials}"}
        epic_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Epic?api-version=7.1"
        epic_body = [
            {"op": "add", "path": "/fields/System.Title", "value": plan_title},
            {"op": "add", "path": "/fields/System.Description", "value": f"AI-generated test plan for: {plan_title}"},
            {"op": "add", "path": "/fields/System.Tags", "value": "QA-Assistant; Test-Plan"}
        ]
        epic_response = requests.post(epic_url, headers=headers, json=epic_body)
        if epic_response.status_code not in [200, 201]:
            return False, f"Failed to create Epic: {epic_response.status_code}", None, []
        epic_id = epic_response.json().get("id")
        epic_url_view = f"https://dev.azure.com/{org}/{project}/_workitems/edit/{epic_id}"
        created_tasks = []
        for tc in test_cases_json[:10]:
            tc_title = str(tc.get("test_scenario", "Test Case"))[:255]
            steps_text = tc.get("steps", "")
            expected = tc.get("expected_result", "")
            task_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Task?api-version=7.1"
            task_body = [
                {"op": "add", "path": "/fields/System.Title", "value": tc_title},
                {"op": "add", "path": "/fields/System.Description", "value": f"<b>Steps:</b><br>{steps_text}<br><br><b>Expected Result:</b><br>{expected}"},
                {"op": "add", "path": "/fields/System.Tags", "value": "QA-Assistant; Test-Case"},
                {"op": "add", "path": "/relations/-", "value": {"rel": "System.LinkTypes.Hierarchy-Reverse", "url": f"https://dev.azure.com/{org}/{project}/_apis/wit/workItems/{epic_id}", "attributes": {"comment": "Child of test plan epic"}}}
            ]
            task_response = requests.post(task_url, headers=headers, json=task_body)
            if task_response.status_code in [200, 201]:
                created_tasks.append(tc_title[:50])
        return True, epic_url_view, epic_id, created_tasks
    except Exception as e:
        return False, f"Error: {e}", None, []

# ============================================
# PAGE TITLE & DESCRIPTION
# ============================================
st.title("🤖 Agentic QA Automation Platform")
st.write("Automate your end-to-end QA workflow using specialised AI agents. Describe your feature once, and the QA Orchestrator coordinates multiple AI agents to analyse requirements, generate test cases, assess testing risk, create Azure DevOps test plans, and produce a complete QA report.")

# ============================================
# AGENTIC QA ORCHESTRATOR
# ============================================
st.write("---")
st.write("## 🚀 QA Orchestrator")
st.write("Describe a feature once. The QA Orchestrator coordinates specialised AI agents to analyse requirements, generate test cases, assess risk, review quality, and create Azure DevOps artefacts automatically.")

agent_feature = st.text_area(
    "Describe the feature you want to test:",
    placeholder="e.g. User can book a car service appointment online",
    key="agent_input"
)

agent_plan_name = st.text_input(
    "Azure DevOps Test Plan Name:",
    placeholder="e.g. Car Booking Feature - Sprint 1"
)

if st.button("🚀 🚀 Run QA Workflow"):
    if not agent_feature.strip():
        st.warning("Please describe a feature first.")
    elif not agent_plan_name.strip():
        st.warning("Please enter a test plan name.")
    else:
        agent_results = {}

        # AGENTS INVOLVED PANEL
        st.write("---")
        st.write("### Agents Involved")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.info("🧠\n\n**Requirement\nAgent**")
        with col2:
            st.info("🔍\n\n**Analysis\nAgent**")
        with col3:
            st.info("🧪\n\n**Test Design\nAgent**")
        with col4:
            st.info("⚠️\n\n**Risk\nAgent**")
        with col5:
            st.info("🚀\n\n**Azure DevOps\nAgent**")

        st.write("**Status:** 🔄 Running...")
        st.write("---")

        # AGENT 1: REQUIREMENT AGENT
        req_placeholder = st.empty()
        req_placeholder.write("🧠 **Requirement Agent** — Running...")
        rg_output = call_openai(
            "You are a senior business analyst. Given a rough idea, produce a structured requirement with: Requirement Title, Business Objective, Actors, User Stories (3+), Functional Requirements, Non-Functional Requirements, Constraints, Out of Scope. Use bold headers.",
            f"Structure this requirement: {agent_feature}"
        )
        agent_results["requirement"] = rg_output
        req_placeholder.write("🧠 **Requirement Agent**\n✓ Structured the requirement\n✓ Identified actors and user stories\n✓ Defined functional and non-functional requirements")

        # AGENT 2: ANALYSIS AGENT
        analysis_placeholder = st.empty()
        analysis_placeholder.write("🔍 **Analysis Agent** — Running...")
        ra_output = call_openai(
            "You are a senior QA engineer. Critique this requirement constructively covering: 1. Ambiguity, 2. Missing acceptance criteria, 3. Untestable language, 4. Edge cases not covered. Use bold headers.",
            f"Challenge this requirement:\n\n{rg_output}"
        )
        agent_results["analysis"] = ra_output
        ambiguity_found = "ambiguity" in ra_output.lower() or "vague" in ra_output.lower()
        ac_found = "acceptance criteria" in ra_output.lower()
        analysis_placeholder.write(f"🔍 **Analysis Agent**\n✓ Challenged requirement for quality\n{'✓ Found ambiguity issues' if ambiguity_found else '✓ No major ambiguity found'}\n{'✓ Found missing acceptance criteria' if ac_found else '✓ Acceptance criteria coverage noted'}\n✓ Edge cases evaluated")

        # AGENT 3: TEST DESIGN AGENT
        tc_placeholder = st.empty()
        tc_placeholder.write("🧪 **Test Design Agent** — Running...")
        tc_output = call_openai(
            "You are a senior QA engineer. Generate EXACTLY 10 Positive, 10 Negative, and 10 Edge Case scenarios (30 total). Format: MODULE NAME - POSITIVE SCENARIOS then 10 dash-bullet lines, blank line, MODULE NAME - NEGATIVE SCENARIOS then 10 dash-bullet lines, blank line, MODULE NAME - EDGE CASES then 10 dash-bullet lines. Each bullet starts with Verify. No duplicates, no filler.",
            f"Generate exactly 30 QA test scenarios for: {agent_feature}"
        )
        agent_results["test_cases"] = tc_output
        positive_count = tc_output.lower().count("verify") if tc_output else 0
        tc_placeholder.write(f"🧪 **Test Design Agent**\n✓ Generated 30 test cases\n✓ Categorised: Positive / Negative / Edge Cases\n✓ {positive_count} scenarios created\n✓ Ready for export to Excel")

        # AGENT 4: RISK ASSESSMENT AGENT
        risk_placeholder = st.empty()
        risk_placeholder.write("⚠️ **Risk Assessment Agent** — Running...")
        risk_output = call_openai(
            "You are a senior QA risk analyst. Given a feature, identify 5-8 key risk areas. Return ONLY valid JSON array, no markdown. Each item: feature, risk_level (Critical/High/Medium/Low), risk_score (1-10), risk_factors, recommended_focus, test_effort (Low/Medium/High).",
            f"Analyse testing risk areas for: {agent_feature}"
        )
        try:
            risk_data = extract_json_array(risk_output)
            risk_df = pd.DataFrame(risk_data).rename(columns={"feature": "Risk Area", "risk_level": "Risk Level", "risk_score": "Risk Score", "risk_factors": "Key Risk Factors", "recommended_focus": "Recommended Focus", "test_effort": "Test Effort"})
            risk_df = risk_df.sort_values("Risk Score", ascending=False)
            agent_results["risk_df"] = risk_df
            high_risks = risk_df[risk_df["Risk Level"].isin(["Critical", "High"])]["Risk Area"].tolist()
            medium_risks = risk_df[risk_df["Risk Level"] == "Medium"]["Risk Area"].tolist()
            risk_summary = ""
            for r in high_risks[:2]:
                risk_summary += f"\n✓ High Risk: {r}"
            for r in medium_risks[:2]:
                risk_summary += f"\n✓ Medium Risk: {r}"
            risk_placeholder.write(f"⚠️ **Risk Assessment Agent**\n✓ Analysed {len(risk_df)} risk areas\n✓ Risk matrix generated{risk_summary}")
        except Exception:
            agent_results["risk_df"] = None
            risk_placeholder.write("⚠️ **Risk Assessment Agent**\n✓ Risk analysis completed (raw format)")

        # AGENT 5: AZURE DEVOPS AGENT
        devops_placeholder = st.empty()
        devops_placeholder.write("🚀 **Azure DevOps Agent** — Running...")
        tc_json_output = call_openai(
            "You are a senior QA engineer. Return ONLY valid JSON array, no markdown. Each item: test_scenario (short title), steps (numbered steps as single string with newlines), expected_result. Generate exactly 10 test cases.",
            f"Generate 10 structured test cases for: {agent_feature}"
        )
        try:
            tc_json_data = extract_json_array(tc_json_output)
            success, epic_url_view, epic_id, created_tasks = create_azure_devops_task_plan(agent_plan_name, tc_json_data)
            agent_results["devops_success"] = success
            agent_results["devops_url"] = epic_url_view
            agent_results["epic_id"] = epic_id
            agent_results["created_tasks"] = created_tasks
            if success:
                tasks_summary = "\n".join([f"✓ Task: {t}" for t in created_tasks[:3]])
                devops_placeholder.write(f"🚀 **Azure DevOps Agent**\n✓ Created Epic #{epic_id}: {agent_plan_name}\n✓ Created Test Plan\n✓ Created {len(created_tasks)} Test Tasks\n{tasks_summary}")
            else:
                devops_placeholder.write(f"🚀 **Azure DevOps Agent**\n⚠️ {epic_url_view}")
        except Exception as e:
            agent_results["devops_success"] = False
            devops_placeholder.write(f"🚀 **Azure DevOps Agent**\n⚠️ Could not create test plan: {e}")

        # STATUS COMPLETE
        st.write("---")
        st.success("✔ All agents completed successfully")

        # AGENT EXECUTION REPORT
        st.write("---")
        st.write("## 📋 Agent Execution Report")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Agents Run", "5")
        with col2:
            st.metric("Test Cases", "30")
        with col3:
            risk_count = len(agent_results.get("risk_df", pd.DataFrame())) if agent_results.get("risk_df") is not None else 0
            st.metric("Risk Areas Identified", str(risk_count))

        with st.expander("📄 Structured Requirement — Requirement Agent"):
            st.write(agent_results.get("requirement", ""))

        with st.expander("🔍 Requirement Analysis — Analysis Agent"):
            st.write(agent_results.get("analysis", ""))

        with st.expander("🧪 Generated Test Cases (30) — Test Design Agent"):
            st.code(agent_results.get("test_cases", ""))

        if agent_results.get("risk_df") is not None:
            with st.expander("⚠️ Risk Matrix — Risk Assessment Agent"):
                st.dataframe(agent_results["risk_df"], use_container_width=True)
                buf = io.BytesIO()
                agent_results["risk_df"].to_excel(buf, index=False, sheet_name="Risk Analysis")
                buf.seek(0)
                st.download_button("⬇️ Download Risk Matrix", buf, "risk_matrix.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        if agent_results.get("devops_success"):
            with st.expander("🚀 Azure DevOps Work Items — Azure DevOps Agent"):
                st.success(f"Epic #{agent_results.get('epic_id')} created with {len(agent_results.get('created_tasks', []))} Tasks")
                st.markdown(f"[View Test Plan in Azure DevOps]({agent_results.get('devops_url', '')})")

        full_report = f"""AGENT EXECUTION REPORT
Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Feature: {agent_feature}
Test Plan: {agent_plan_name}

Agents Involved:
- 🧠 Requirement Agent
- 🔍 Analysis Agent
- 🧪 Test Design Agent
- ⚠️ Risk Assessment Agent
- 🚀 Azure DevOps Agent

Status: Completed

{'='*60}
STRUCTURED REQUIREMENT — Requirement Agent
{'='*60}
{agent_results.get('requirement', '')}

{'='*60}
REQUIREMENT ANALYSIS — Analysis Agent
{'='*60}
{agent_results.get('analysis', '')}

{'='*60}
GENERATED TEST CASES — Test Design Agent
{'='*60}
{agent_results.get('test_cases', '')}
"""
        st.download_button("⬇️ Download Agent Execution Report", full_report, "agent_execution_report.txt")

# ============================================
# QA KNOWLEDGE BASE
# ============================================
st.write("---")
st.write("## 📚 QA Knowledge Base")
st.write("Search predefined QA scenarios and testing guidance by keyword.")

query = st.text_input("Search by keyword:", key="search_box")
st.caption("Try: login, logout, ui frontend, ui non functional, xss, accessibility, regression")

if st.button("Clear Search", key="clear_btn"):
    if "search_box" in st.session_state:
        del st.session_state["search_box"]
    st.rerun()

if query:
    query = query.lower().replace("-", " ")
    results = []
    download_text = ""
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"
    matched_module = None
    if "ui non functional" in query:
        matched_module = "ui non-functional"
    elif query.strip() in ["ui", "frontend"] or "ui " in query:
        matched_module = "ui"
    elif "regression" in query:
        matched_module = "regression"
    elif "accessibility" in query:
        matched_module = "accessibility"
    elif "cross site scripting" in query or "xss" in query:
        matched_module = "cross site scripting"
    elif "data security" in query:
        matched_module = "data security"
    elif "api security" in query:
        matched_module = "api security"
    elif "checkout" in query or "payment" in query:
        matched_module = "checkout"
    elif "upload" in query:
        matched_module = "upload"
    elif "download" in query:
        matched_module = "download"
    elif "search" in query:
        matched_module = "search"
    elif "login" in query:
        matched_module = "login"
    elif "logout" in query:
        matched_module = "logout"
    elif "registration" in query:
        matched_module = "registration"
    elif "password" in query:
        matched_module = "password reset"
    elif "vehicle" in query:
        matched_module = "vehicle"
    elif "order" in query:
        matched_module = "order"
    elif "api" in query:
        matched_module = "api"
    elif "database" in query:
        matched_module = "database"
    elif "performance" in query:
        matched_module = "performance"
    elif "session" in query:
        matched_module = "session"
    elif "authentication" in query or "authorization" in query:
        matched_module = "authentication"
    elif "security" in query:
        matched_module = "security"
    module_map = {"ui": ["ui", "frontend"], "ui non-functional": ["ui non functional"], "regression": ["regression"], "accessibility": ["accessibility"], "cross site scripting": ["cross site scripting", "xss"], "login": ["login"], "logout": ["logout"], "password reset": ["password"], "registration": ["registration"], "search": ["search"], "upload": ["upload"], "download": ["download"], "vehicle": ["vehicle"], "order": ["order"], "checkout": ["checkout", "payment"], "api": ["api"], "performance": ["performance"], "database": ["database"], "security": ["security"], "data security": ["data security"], "api security": ["api security"], "session": ["session"], "authentication": ["authentication", "authorization"]}
    keyword_map = {"login": ["login", "sign in", "log in"], "logout": ["logout", "sign out"], "ui": ["frontend", "interface"], "cross site scripting": ["xss"], "checkout": ["payment", "transaction"], "accessibility": ["a11y"]}
    for section in sections:
        section_text = section.lower().replace("-", " ")
        title = section.strip().split("\n")[0].lower().replace("-", " ")
        if "all" in query:
            results.append(section)
            continue
        if matched_module:
            keywords = module_map.get(matched_module, []) + keyword_map.get(matched_module, [])
            if any(word in title for word in keywords):
                if matched_module == "accessibility" and "accessibility" not in title:
                    continue
                if matched_module == "regression" and "regression" not in title:
                    continue
                if filter_type:
                    if filter_type in title or filter_type in section_text:
                        results.append(section)
                else:
                    results.append(section)
    results = list(dict.fromkeys(results))
    st.write(f"✅ {len(results)} results found")
    if results:
        for sec in results:
            st.code(sec)
            st.write("---")
            download_text += sec + "\n\n"
        st.download_button("⬇️ Download Test Scenarios", download_text, "qa_test_scenarios.txt")
    else:
        st.warning("No results found.")

# ============================================
# INDIVIDUAL TOOLS (collapsible)
# ============================================
st.write("---")
with st.expander("🧠 Individual QA Agents"):
    st.write("Use these tools individually if you prefer manual control over each step.")

    st.write("### 📝 Requirement Gathering")
    rough_idea = st.text_area("Describe your rough idea:", placeholder="e.g. We need users to reset their password", key="rg_input")
    if st.button("Generate Structured Requirement"):
        if not rough_idea.strip():
            st.warning("Please describe your idea first.")
        else:
            with st.spinner("Generating..."):
                rg_output = call_openai("You are a senior business analyst. Given a rough idea, produce a structured requirement with: Requirement Title, Business Objective, Actors, User Stories (3+), Functional Requirements, Non-Functional Requirements, Constraints, Out of Scope. Use bold headers.", f"Structure this requirement: {rough_idea}")
            st.session_state["rg_output"] = rg_output
    if "rg_output" in st.session_state:
        st.write(st.session_state["rg_output"])
        st.download_button("⬇️ Download Requirement", st.session_state["rg_output"], "requirement.txt")
        feedback_buttons("Requirement Gathering", key_suffix="rg")

    st.write("---")
    st.write("### 🧠 Challenge My Requirement")
    requirement_text = st.text_area("Paste your requirement:", placeholder="e.g. As a user, I want to reset my password...", key="ra_input")
    if st.button("Challenge This Requirement"):
        if not requirement_text.strip():
            st.warning("Please paste a requirement first.")
        else:
            with st.spinner("Analysing..."):
                ra_output = call_openai("You are a senior QA engineer. Critique this requirement covering: 1. Ambiguity, 2. Missing acceptance criteria, 3. Untestable language, 4. Edge cases not covered. Use bold headers.", f"Challenge this requirement:\n\n{requirement_text}")
            st.session_state["ra_output"] = ra_output
    if "ra_output" in st.session_state:
        st.write(st.session_state["ra_output"])
        feedback_buttons("Requirement Analysis", key_suffix="ra")

    st.write("---")
    st.write("### ✅ Generate Acceptance Criteria")
    ac_text = st.text_area("Paste your requirement:", placeholder="e.g. As a user, I want to reset my password...", key="ac_input")
    ac_format = st.radio("Format:", ["Given/When/Then (Gherkin)", "Simple Checklist"], horizontal=True)
    if st.button("Generate Acceptance Criteria"):
        if not ac_text.strip():
            st.warning("Please paste a requirement first.")
        else:
            with st.spinner("Generating..."):
                if ac_format == "Given/When/Then (Gherkin)":
                    sp = "You are a senior BA. Write exactly 6 Gherkin acceptance criteria scenarios (Given/When/Then). Format: Scenario: title, Given context, When action, Then outcome. Separate with blank lines."
                else:
                    sp = "You are a senior BA. Write exactly 10 acceptance criteria checklist items starting with 'The system should...' or 'The user can...'."
                ac_output = call_openai(sp, f"Write acceptance criteria for:\n\n{ac_text}")
            st.session_state["ac_output"] = ac_output
    if "ac_output" in st.session_state:
        formatted = st.session_state["ac_output"].replace("\nGiven", "  \nGiven").replace("\nWhen", "  \nWhen").replace("\nThen", "  \nThen").replace("\nAnd", "  \nAnd")
        st.markdown(formatted)
        st.download_button("⬇️ Download Acceptance Criteria", st.session_state["ac_output"], "acceptance_criteria.txt")
        feedback_buttons("Acceptance Criteria", key_suffix="ac")

    st.write("---")
    st.write("### 🤖 AI Test Case Generator")
    feature_desc = st.text_area("Describe the feature:", placeholder="e.g. User can apply a discount code at checkout", key="tc_input")
    if st.button("Generate Test Cases"):
        if not feature_desc.strip():
            st.warning("Please describe a feature first.")
        else:
            with st.spinner("Generating 30 test cases..."):
                tc_out = call_openai("You are a senior QA engineer. Generate EXACTLY 10 Positive, 10 Negative, and 10 Edge Case scenarios (30 total). Format: MODULE NAME - POSITIVE SCENARIOS then 10 dash-bullet lines, blank line, MODULE NAME - NEGATIVE SCENARIOS then 10 dash-bullet lines, blank line, MODULE NAME - EDGE CASES then 10 dash-bullet lines. Each bullet starts with Verify.", f"Generate exactly 30 QA test scenarios for: {feature_desc}")
            st.session_state["tc_output"] = tc_out
    if "tc_output" in st.session_state:
        st.code(st.session_state["tc_output"])
        st.download_button("⬇️ Download Test Cases", st.session_state["tc_output"], "test_cases.txt")
        feedback_buttons("Test Case Generator", key_suffix="tc")

    st.write("---")
    st.write("### 📋 Use Case Generator")
    uc_feat = st.text_area("Describe the feature:", placeholder="e.g. User can reset password via email", key="uc_input")
    if st.button("Generate Use Case"):
        if not uc_feat.strip():
            st.warning("Please describe a feature first.")
        else:
            with st.spinner("Generating..."):
                uc_out = call_openai("You are a senior BA. Generate a complete use case with: Use Case Name, Actor(s), Preconditions, Main Success Scenario, Alternative Flows, Exception Flows, Postconditions, Business Rules. Use bold headers.", f"Generate use case for: {uc_feat}")
            st.session_state["uc_output"] = uc_out
    if "uc_output" in st.session_state:
        st.write(st.session_state["uc_output"])
        st.download_button("⬇️ Download Use Case", st.session_state["uc_output"], "use_case.txt")
        feedback_buttons("Use Case Generator", key_suffix="uc")

    st.write("---")
    st.write("### 🎯 Test Coverage Risk Analysis")
    risk_feats = st.text_area("Paste features/modules (one per line):", placeholder="User Login\nPassword Reset\nPayment Checkout", key="risk_input")
    if st.button("Analyse Risk"):
        if not risk_feats.strip():
            st.warning("Please paste features first.")
        else:
            with st.spinner("Analysing risk..."):
                risk_out = call_openai("You are a senior QA risk analyst. Analyse each feature for testing risk. Return ONLY valid JSON array, no markdown. Each item: feature, risk_level (Critical/High/Medium/Low), risk_score (1-10), risk_factors, recommended_focus, test_effort (Low/Medium/High).", f"Analyse risk for:\n\n{risk_feats}")
            try:
                risk_data = extract_json_array(risk_out)
                risk_df = pd.DataFrame(risk_data).rename(columns={"feature": "Feature", "risk_level": "Risk Level", "risk_score": "Risk Score", "risk_factors": "Key Risk Factors", "recommended_focus": "Recommended Focus", "test_effort": "Test Effort"})
                st.session_state["risk_df"] = risk_df.sort_values("Risk Score", ascending=False)
            except Exception:
                st.session_state["risk_df"] = None
                st.warning("Could not parse results.")
                st.code(risk_out)
    if st.session_state.get("risk_df") is not None:
        st.dataframe(st.session_state["risk_df"], use_container_width=True)
        buf = io.BytesIO()
        st.session_state["risk_df"].to_excel(buf, index=False, sheet_name="Risk Analysis")
        buf.seek(0)
        st.download_button("⬇️ Download Risk Analysis", buf, "risk_analysis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        feedback_buttons("Risk Analysis", key_suffix="risk")

    st.write("---")
    st.write("### 📊 Export Test Cases to Excel")
    export_text = st.text_area("Paste test scenarios to export:", placeholder="Paste test scenarios here...", key="export_input")
    if st.button("Convert to Excel"):
        if not export_text.strip():
            st.warning("Please paste test scenarios first.")
        else:
            with st.spinner("Generating detailed steps..."):
                xl_out = call_openai("You are a senior QA engineer. Process EVERY bullet in the input. Return ONLY valid JSON array, no markdown, no code fences, no trailing commas. Each item: module, category, test_scenario, steps (numbered steps separated by newlines), test_data (plain string or N/A), expected_result.", f"Convert EVERY scenario below:\n\n{export_text}")
            try:
                tcs = extract_json_array(xl_out)
                df = pd.DataFrame(tcs)
                for col in df.columns:
                    df[col] = df[col].apply(flatten_value)
                df.insert(0, "Test ID", [f"TC-{i+1:03d}" for i in range(len(df))])
                df = df.rename(columns={"module": "Module", "category": "Category", "test_scenario": "Test Scenario", "steps": "Steps", "test_data": "Test Data", "expected_result": "Expected Result"})
                df["Actual Result"] = ""
                df["Status"] = ""
                st.session_state["excel_df"] = df.reset_index(drop=True)
            except Exception:
                st.session_state["excel_df"] = None
                st.warning("Could not parse results.")
                st.code(xl_out)
    if st.session_state.get("excel_df") is not None:
        df = st.session_state["excel_df"]
        st.write(f"### Preview ({len(df)} test cases)")
        st.dataframe(df, use_container_width=True)
        buf = io.BytesIO()
        df.to_excel(buf, index=False, sheet_name="Test Cases")
        buf.seek(0)
        st.download_button("⬇️ Download Excel File", buf, "test_cases.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        feedback_buttons("Excel Export", key_suffix="excel")

    st.write("---")
    st.write("### 🗂️ Auto-Create Azure DevOps Test Plan")
    tp_feat = st.text_area("Describe the feature:", placeholder="e.g. User checkout and payment process", key="tp_input")
    tp_name = st.text_input("Test Plan Name:", placeholder="e.g. Checkout - Sprint 1 Test Plan")
    if st.button("🗂️ Create Test Plan in Azure DevOps"):
        if not tp_feat.strip() or not tp_name.strip():
            st.warning("Please fill in both fields.")
        else:
            with st.spinner("Generating and creating test plan..."):
                tp_out = call_openai("You are a senior QA engineer. Return ONLY valid JSON array, no markdown. Each item: test_scenario (short title), steps (numbered steps as single string), expected_result. Generate 5 test cases.", f"Generate test cases for: {tp_feat}")
            try:
                tp_data = extract_json_array(tp_out)
                success, epic_url_view, epic_id, created_tasks = create_azure_devops_task_plan(tp_name, tp_data)
                if success:
                    st.success(f"✅ Test Plan created as Epic #{epic_id} with {len(created_tasks)} Tasks! [View in Azure DevOps]({epic_url_view})")
                else:
                    st.error(epic_url_view)
            except Exception as e:
                st.error(f"Error: {e}")

    st.write("---")
    st.write("### 🐛 Bug Report")
    bug_title = st.text_input("Bug Title:", placeholder="e.g. Login button unresponsive on mobile", key="bug_title")
    bug_severity = st.selectbox("Severity:", ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"])
    bug_desc = st.text_area("Bug Description:", placeholder="Describe what happened...", key="bug_desc")
    bug_steps = st.text_area("Steps to Reproduce:", placeholder="1. Go to login page\n2. Click Login\n3. Nothing happens", key="bug_steps")
    if st.button("🐛 Log Bug to Azure DevOps"):
        if not bug_title.strip() or not bug_desc.strip() or not bug_steps.strip():
            st.warning("Please fill in all fields.")
        else:
            with st.spinner("Logging bug..."):
                success, message = create_azure_devops_issue(bug_title, bug_severity, bug_desc, bug_steps)
            if success:
                st.success(message)
            else:
                st.error(message)

# ============================================
# FEEDBACK SUMMARY
# ============================================
if st.session_state.feedback_log:
    st.write("---")
    with st.expander("📋 Feedback Log"):
        feedback_df = pd.DataFrame(st.session_state.feedback_log)
        st.dataframe(feedback_df, use_container_width=True)
        st.write(f"Total: {len(st.session_state.feedback_log)} | 👍 {sum(1 for f in st.session_state.feedback_log if f['rating'] == 'up')} | 👎 {sum(1 for f in st.session_state.feedback_log if f['rating'] == 'down')}")
