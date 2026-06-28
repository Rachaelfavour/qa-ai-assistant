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
            return True, f"✅ Issue #{work_item_id} created successfully! [View in Azure DevOps]({work_item_url})"
        else:
            return False, f"Failed to create issue: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error: {e}"

def create_azure_devops_task_plan(plan_title, test_cases_json):
    try:
        pat = st.secrets.get("AZURE_DEVOPS_PAT")
        org = "richkome"
        project = "QA-Assistant"
        if not pat:
            return False, "Azure DevOps PAT not found in Streamlit secrets."
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
            return False, f"Failed to create Epic: {epic_response.status_code} - {epic_response.text}"
        epic_id = epic_response.json().get("id")
        epic_url_view = f"https://dev.azure.com/{org}/{project}/_workitems/edit/{epic_id}"
        created_count = 0
        for tc in test_cases_json[:10]:
            tc_title = str(tc.get("test_scenario", tc.get("Test Scenario", "Test Case")))[:255]
            steps_text = tc.get("steps", tc.get("Steps", ""))
            expected = tc.get("expected_result", tc.get("Expected Result", ""))
            description_html = f"<b>Steps:</b><br>{steps_text}<br><br><b>Expected Result:</b><br>{expected}"
            task_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Task?api-version=7.1"
            task_body = [
                {"op": "add", "path": "/fields/System.Title", "value": tc_title},
                {"op": "add", "path": "/fields/System.Description", "value": description_html},
                {"op": "add", "path": "/fields/System.Tags", "value": "QA-Assistant; Test-Case"},
                {"op": "add", "path": "/relations/-", "value": {"rel": "System.LinkTypes.Hierarchy-Reverse", "url": f"https://dev.azure.com/{org}/{project}/_apis/wit/workItems/{epic_id}", "attributes": {"comment": "Child of test plan epic"}}}
            ]
            task_response = requests.post(task_url, headers=headers, json=task_body)
            if task_response.status_code in [200, 201]:
                created_count += 1
        return True, f"✅ Test Plan created as Epic #{epic_id} with {created_count} Tasks! [View in Azure DevOps]({epic_url_view})"
    except Exception as e:
        return False, f"Error: {e}"

st.title("QA Assistant Chatbot 🤖")
st.write("Search or select a module to view QA test scenarios.")

query = st.text_input("Search or ask a QA question:", key="search_box")
st.caption("Try: login, logout, ui frontend, ui non functional, xss, accessibility, regression")

if st.button("Clear Search", key="clear_btn"):
    if "search_box" in st.session_state:
        del st.session_state["search_box"]
    st.rerun()

if query:
    query = query.lower().replace("-", " ")
    st.write("### Suggested Test Scenarios")
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
        st.warning("No results found. Try using different keywords or select a module.")

# ============================================
# REQUIREMENT GATHERING
# ============================================
st.write("---")
st.write("## 📝 Requirement Gathering")
st.write("Describe a rough idea or business need. AI will turn it into a properly structured requirement with user stories, actors, and goals.")

rough_idea = st.text_area(
    "Describe your rough idea or business need:",
    placeholder="e.g. We need users to be able to reset their password if they forget it",
    key="rg_input"
)

if st.button("Generate Structured Requirement"):
    if not rough_idea.strip():
        st.warning("Please describe your idea first.")
    else:
        with st.spinner("Generating structured requirement..."):
            system_prompt = "You are a senior business analyst. Given a rough idea or business need, produce a complete, well-structured software requirement document with these exact sections: 1. Requirement Title, 2. Business Objective (why this is needed), 3. Actors (who is involved), 4. User Stories (at least 3, in 'As a... I want to... So that...' format), 5. Functional Requirements (numbered list of what the system must do), 6. Non-Functional Requirements (performance, security, usability), 7. Constraints and Assumptions, 8. Out of Scope. Format each section with a clear bold header. Be specific and professional."
            user_prompt = f"Turn this rough idea into a structured requirement:\n\n{rough_idea}"
            rg_output = call_openai(system_prompt, user_prompt)

        st.session_state["rg_output"] = rg_output
        st.session_state["rg_idea"] = rough_idea

if "rg_output" in st.session_state:
    st.write("### Structured Requirement")
    st.write(st.session_state["rg_output"])
    st.download_button(
        "⬇️ Download Requirement Document",
        st.session_state["rg_output"],
        "requirement_document.txt"
    )
    feedback_buttons("Requirement Gathering", st.session_state.get("rg_idea", ""), key_suffix="rg")

# ============================================
# AI REQUIREMENT ANALYSIS ("CHALLENGE MY REQUIREMENT")
# ============================================
st.write("---")
st.write("## 🧠 Challenge My Requirement")
st.write("Paste a requirement or user story. AI will critique it for ambiguity, missing acceptance criteria, and untestable language.")

requirement_text = st.text_area(
    "Paste your requirement or user story:",
    placeholder="e.g. As a user, I want to reset my password so I can log back in."
)

if st.button("Challenge This Requirement"):
    if not requirement_text.strip():
        st.warning("Please paste a requirement first.")
    else:
        with st.spinner("Analyzing requirement..."):
            system_prompt = "You are a senior QA engineer reviewing a requirement or user story before it goes into development. Critique it constructively. Cover: 1. Ambiguity - any vague or unclear wording. 2. Missing acceptance criteria - what's not defined. 3. Untestable language - words that can't be verified objectively. 4. Edge cases not covered - what scenarios are missing. Format your response with clear headers for each section above. Be specific and constructive, not just critical."
            user_prompt = f"Challenge this requirement:\n\n{requirement_text}"
            analysis_output = call_openai(system_prompt, user_prompt)

        st.session_state["ra_output"] = analysis_output
        st.session_state["ra_requirement"] = requirement_text

if "ra_output" in st.session_state:
    st.write("### Requirement Analysis")
    st.write(st.session_state["ra_output"])
    feedback_buttons("Requirement Analysis", st.session_state.get("ra_requirement", ""), key_suffix="ra")

# ============================================
# AI ACCEPTANCE CRITERIA GENERATOR
# ============================================
st.write("---")
st.write("## ✅ Generate Acceptance Criteria")
st.write("Paste a requirement or user story. AI will generate clear acceptance criteria in your chosen format.")

ac_requirement_text = st.text_area(
    "Paste your requirement or user story:",
    placeholder="e.g. As a user, I want to reset my password so I can log back in.",
    key="ac_input"
)

ac_format = st.radio("Choose format:", ["Given/When/Then (Gherkin)", "Simple Checklist"], horizontal=True)

if st.button("Generate Acceptance Criteria"):
    if not ac_requirement_text.strip():
        st.warning("Please paste a requirement first.")
    else:
        with st.spinner("Generating acceptance criteria..."):
            if ac_format == "Given/When/Then (Gherkin)":
                system_prompt = "You are a senior business analyst. Given a requirement or user story, write clear acceptance criteria in Gherkin format (Given/When/Then). You MUST produce EXACTLY 6 scenarios, no fewer - covering the main happy path, validation and error cases, and edge cases. Count your scenarios before finishing; if you have fewer than 6, add more. Format each scenario as: Scenario: <short title>, then Given <context>, When <action>, Then <expected outcome>. Separate scenarios with a blank line."
            else:
                system_prompt = "You are a senior business analyst. Given a requirement or user story, write clear acceptance criteria as a simple checklist. You MUST produce EXACTLY 10 checklist items, no fewer, covering the main happy path, validation, and edge cases. Count your items before finishing; if you have fewer than 10, add more. Each line should be a single, testable, unambiguous criterion starting with 'The system should...' or 'The user can...'."
            user_prompt = f"Write acceptance criteria for this requirement:\n\n{ac_requirement_text}"
            ac_output = call_openai(system_prompt, user_prompt)

        st.session_state["ac_output"] = ac_output
        st.session_state["ac_requirement"] = ac_requirement_text

if "ac_output" in st.session_state:
    st.write("### Generated Acceptance Criteria")
    formatted_output = st.session_state["ac_output"].replace("\nGiven", "  \nGiven").replace("\nWhen", "  \nWhen").replace("\nThen", "  \nThen").replace("\nAnd", "  \nAnd")
    st.markdown(formatted_output)
    st.download_button("⬇️ Download Acceptance Criteria", st.session_state["ac_output"], "acceptance_criteria.txt")
    feedback_buttons("Acceptance Criteria Generator", st.session_state.get("ac_requirement", ""), key_suffix="ac")

# ============================================
# AI TEST CASE GENERATION
# ============================================
st.write("---")
st.write("## 🤖 AI Test Case Generator")
st.write("Describe a feature and get fresh AI-generated test scenarios in the same style as above.")

feature_description = st.text_area("Describe the feature to test:", placeholder="e.g. User can apply a discount code at checkout")

if st.button("Generate Test Cases with AI"):
    if not feature_description.strip():
        st.warning("Please describe a feature first.")
    else:
        with st.spinner("Generating test cases..."):
            system_prompt = "You are a senior QA engineer. You MUST generate EXACTLY 10 Positive scenarios, EXACTLY 10 Negative scenarios, and EXACTLY 10 Edge Case scenarios. That is 30 scenarios total, no fewer. This is a strict requirement, not a suggestion. Count your bullets before finishing. If you have fewer than 10 in any category, add more before stopping. Format your output EXACTLY like this: MODULE NAME - POSITIVE SCENARIOS then 10 lines each starting with a dash, then a blank line, then MODULE NAME - NEGATIVE SCENARIOS then 10 lines each starting with a dash, then a blank line, then MODULE NAME - EDGE CASES then 10 lines each starting with a dash. Replace MODULE NAME with the feature name. Each bullet must be a distinct, specific, realistic scenario, no duplicates, no filler. Start each with Verify where natural."
            user_prompt = f"Generate exactly 30 QA test scenarios (10 positive, 10 negative, 10 edge cases) for this feature: {feature_description}"
            ai_output = call_openai(system_prompt, user_prompt)

        st.session_state["tc_output"] = ai_output
        st.session_state["tc_feature"] = feature_description

if "tc_output" in st.session_state:
    st.write("### Generated Test Scenarios")
    st.code(st.session_state["tc_output"])
    st.download_button("⬇️ Download AI Test Scenarios", st.session_state["tc_output"], "ai_generated_test_scenarios.txt")
    feedback_buttons("Test Case Generator", st.session_state.get("tc_feature", ""), key_suffix="tc")

# ============================================
# USE CASE GENERATOR
# ============================================
st.write("---")
st.write("## 📋 Use Case Generator")
st.write("Describe a feature and AI will generate a structured use case document.")

uc_feature = st.text_area("Describe the feature:", placeholder="e.g. User can reset their password via email link", key="uc_input")

if st.button("Generate Use Case"):
    if not uc_feature.strip():
        st.warning("Please describe a feature first.")
    else:
        with st.spinner("Generating use case..."):
            system_prompt = "You are a senior business analyst. Given a feature description, generate a complete, structured use case document with these exact sections: Use Case Name, Actor(s), Preconditions, Main Success Scenario (numbered steps), Alternative Flows (numbered), Exception Flows (numbered), Postconditions, and Business Rules. Be specific, realistic and thorough. Format each section with a clear bold header."
            user_prompt = f"Generate a full structured use case for this feature: {uc_feature}"
            uc_output = call_openai(system_prompt, user_prompt)

        st.session_state["uc_output"] = uc_output
        st.session_state["uc_feature"] = uc_feature

if "uc_output" in st.session_state:
    st.write("### Generated Use Case")
    st.write(st.session_state["uc_output"])
    st.download_button("⬇️ Download Use Case", st.session_state["uc_output"], "use_case.txt")
    feedback_buttons("Use Case Generator", st.session_state.get("uc_feature", ""), key_suffix="uc")

# ============================================
# TEST COVERAGE RISK ANALYSIS
# ============================================
st.write("---")
st.write("## 🎯 Test Coverage Risk Analysis")
st.write("Paste a list of features or modules. AI will predict which are highest risk and need the most testing attention.")

risk_features = st.text_area("Paste your features/modules (one per line):", placeholder="e.g.\nUser Login\nPassword Reset\nPayment Checkout\nProduct Search\nUser Profile\nAdmin Dashboard", key="risk_input")

if st.button("Analyse Risk"):
    if not risk_features.strip():
        st.warning("Please paste a list of features first.")
    else:
        with st.spinner("Analysing test coverage risk..."):
            system_prompt = "You are a senior QA engineer and risk analyst. Given a list of software features or modules, analyse each one for testing risk. For each feature, provide: Risk Level (Critical/High/Medium/Low), Risk Score (1-10), Key Risk Factors (why it is risky), Recommended Test Focus (what types of testing to prioritise), and Estimated Test Effort (Low/Medium/High). Return ONLY a valid JSON array with no markdown, no code fences, no commentary. Each item must have exactly these fields: feature, risk_level, risk_score, risk_factors, recommended_focus, test_effort."
            user_prompt = f"Analyse the testing risk for each of these features:\n\n{risk_features}"
            risk_output = call_openai(system_prompt, user_prompt)

        try:
            risk_data = extract_json_array(risk_output)
            risk_df = pd.DataFrame(risk_data)
            risk_df = risk_df.rename(columns={"feature": "Feature", "risk_level": "Risk Level", "risk_score": "Risk Score", "risk_factors": "Key Risk Factors", "recommended_focus": "Recommended Test Focus", "test_effort": "Test Effort"})
            risk_df = risk_df.sort_values("Risk Score", ascending=False)
            st.session_state["risk_df"] = risk_df
        except Exception:
            st.session_state["risk_df"] = None
            st.session_state["risk_raw"] = risk_output

if st.session_state.get("risk_df") is not None:
    df = st.session_state["risk_df"]
    st.write("### Risk Analysis Results")
    st.dataframe(df, use_container_width=True)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Risk Analysis")
    buffer.seek(0)
    st.download_button("⬇️ Download Risk Analysis (Excel)", buffer, "test_coverage_risk.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    feedback_buttons("Risk Analysis", key_suffix="risk")
elif "risk_raw" in st.session_state:
    st.warning("Could not parse risk analysis. Raw response below:")
    st.code(st.session_state["risk_raw"])

# ============================================
# AUTO-CREATE AZURE DEVOPS TEST PLAN (as Epic + Tasks)
# ============================================
st.write("---")
st.write("## 🗂️ Auto-Create Azure DevOps Test Plan")
st.write("Describe a feature. AI generates test cases and automatically creates an Epic with linked Tasks in Azure DevOps.")

tp_feature = st.text_area("Describe the feature to create a test plan for:", placeholder="e.g. User checkout and payment process", key="tp_input")
tp_plan_name = st.text_input("Test Plan Name:", placeholder="e.g. Checkout Feature - Sprint 1 Test Plan")

if st.button("🗂️ Generate & Create Test Plan in Azure DevOps"):
    if not tp_feature.strip():
        st.warning("Please describe a feature first.")
    elif not tp_plan_name.strip():
        st.warning("Please enter a test plan name.")
    else:
        with st.spinner("Generating test cases and creating Azure DevOps Test Plan..."):
            system_prompt = "You are a senior QA engineer. Generate structured test cases for the given feature. Return ONLY a valid JSON array with no markdown, no code fences. Each item must have exactly these fields: test_scenario (short title), steps (numbered steps as a single string separated by newlines), expected_result (single string). Generate at least 5 test cases covering positive, negative and edge scenarios."
            user_prompt = f"Generate structured test cases for: {tp_feature}"
            tc_output = call_openai(system_prompt, user_prompt)

        try:
            tc_data = extract_json_array(tc_output)
            success, message = create_azure_devops_task_plan(tp_plan_name, tc_data)
            if success:
                st.success(message)
                st.write("### Test Cases Created:")
                tc_df = pd.DataFrame(tc_data)
                st.dataframe(tc_df, use_container_width=True)
            else:
                st.error(message)
        except Exception as e:
            st.error(f"Could not parse test cases: {e}")
            st.code(tc_output)

# ============================================
# STRUCTURED OUTPUT: EXCEL EXPORT (AI-POWERED STEPS)
# ============================================
st.write("---")
st.write("## 📊 Export Test Cases to Excel")
st.write("Paste any test scenario text. AI will fill in real Steps, Test Data, and Expected Results, then export to Excel.")

export_text = st.text_area("Paste test scenarios to export:", placeholder="Paste AI-generated or existing test scenarios here...")

if st.button("Convert to Excel"):
    if not export_text.strip():
        st.warning("Please paste some test scenarios first.")
    else:
        with st.spinner("Generating detailed steps, test data and expected results..."):
            system_prompt = "You are a senior QA engineer. You will be given a block of test scenario text, organized under headers like MODULE NAME - CATEGORY followed by dash-bulleted scenarios. You MUST process EVERY SINGLE bullet line in the input, do not skip or summarize any of them. For each individual bullet scenario, produce a structured test case with specific, actionable steps using concrete field names, button labels, and exact user actions. Each test case should have between 3 and 7 steps depending on complexity. For test_data, always use a single plain string value, never a nested object. If no specific data applies, use the string N/A in quotes. Return ONLY a valid JSON array, with absolutely no markdown formatting, no code fences, no commentary before or after, and no trailing commas. Each item in the array must have exactly these fields: module, category, test_scenario (the original bullet text), steps (numbered steps separated by newlines), test_data (a plain string), expected_result."
            user_prompt = f"Convert EVERY scenario below into a structured test case:\n\n{export_text}"
            ai_output = call_openai(system_prompt, user_prompt)

        try:
            test_cases = extract_json_array(ai_output)
            df = pd.DataFrame(test_cases)
            for col in df.columns:
                df[col] = df[col].apply(flatten_value)
            df.insert(0, "Test ID", [f"TC-{i+1:03d}" for i in range(len(df))])
            df = df.rename(columns={"module": "Module", "category": "Category", "test_scenario": "Test Scenario", "steps": "Steps", "test_data": "Test Data", "expected_result": "Expected Result"})
            df["Actual Result"] = ""
            df["Status"] = ""
            st.session_state["excel_df"] = df
        except Exception:
            st.session_state["excel_df"] = None
            st.session_state["excel_raw"] = ai_output

if st.session_state.get("excel_df") is not None:
    df = st.session_state["excel_df"]
    df = df.reset_index(drop=True)
    st.write(f"### Preview ({len(df)} test cases)")
    st.dataframe(df, use_container_width=True)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Test Cases")
    buffer.seek(0)
    st.download_button("⬇️ Download Excel File", buffer, "test_cases.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    feedback_buttons("Excel Export", key_suffix="excel")
elif "excel_raw" in st.session_state:
    st.warning("AI response couldn't be parsed into a table. Raw response below:")
    st.code(st.session_state["excel_raw"])

# ============================================
# BUG REPORT — LOGS TO AZURE DEVOPS
# ============================================
st.write("---")
st.write("## 🐛 Bug Report")
st.write("Log a bug directly to Azure DevOps as a Work Item.")

bug_title = st.text_input("Bug Title:", placeholder="e.g. Login button unresponsive on mobile")
bug_severity = st.selectbox("Severity:", ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"])
bug_description = st.text_area("Bug Description:", placeholder="Describe what happened...")
bug_steps = st.text_area("Steps to Reproduce:", placeholder="1. Go to login page\n2. Enter valid credentials\n3. Click Login button\n4. Nothing happens")

if st.button("🐛 Log Bug to Azure DevOps"):
    if not bug_title.strip():
        st.warning("Please enter a bug title.")
    elif not bug_description.strip():
        st.warning("Please enter a bug description.")
    elif not bug_steps.strip():
        st.warning("Please enter steps to reproduce.")
    else:
        with st.spinner("Logging bug to Azure DevOps..."):
            success, message = create_azure_devops_issue(title=bug_title, severity=bug_severity, description=bug_description, steps_to_reproduce=bug_steps)
        if success:
            st.success(message)
        else:
            st.error(message)

# ============================================
# FEEDBACK SUMMARY (ADMIN VIEW)
# ============================================
if st.session_state.feedback_log:
    st.write("---")
    with st.expander("📋 View Feedback Log (for demo/admin purposes)"):
        feedback_df = pd.DataFrame(st.session_state.feedback_log)
        st.dataframe(feedback_df, use_container_width=True)
        st.write(f"Total feedback collected: {len(st.session_state.feedback_log)}")
        st.write(f"👍 Positive: {sum(1 for f in st.session_state.feedback_log if f['rating'] == 'up')}")
        st.write(f"👎 Negative: {sum(1 for f in st.session_state.feedback_log if f['rating'] == 'down')}")
