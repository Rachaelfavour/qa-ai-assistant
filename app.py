import streamlit as st
import re
import json
import pandas as pd
import io
import datetime
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

    module_map = {
        "ui": ["ui", "frontend"],
        "ui non-functional": ["ui non functional"],
        "regression": ["regression"],
        "accessibility": ["accessibility"],
        "cross site scripting": ["cross site scripting", "xss"],
        "login": ["login"],
        "logout": ["logout"],
        "password reset": ["password"],
        "registration": ["registration"],
        "search": ["search"],
        "upload": ["upload"],
        "download": ["download"],
        "vehicle": ["vehicle"],
        "order": ["order"],
        "checkout": ["checkout", "payment"],
        "api": ["api"],
        "performance": ["performance"],
        "database": ["database"],
        "security": ["security"],
        "data security": ["data security"],
        "api security": ["api security"],
        "session": ["session"],
        "authentication": ["authentication", "authorization"]
    }

    keyword_map = {
        "login": ["login", "sign in", "log in"],
        "logout": ["logout", "sign out"],
        "ui": ["frontend", "interface"],
        "cross site scripting": ["xss"],
        "checkout": ["payment", "transaction"],
        "accessibility": ["a11y"]
    }

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

        st.download_button(
            "⬇️ Download Test Scenarios",
            download_text,
            "qa_test_scenarios.txt"
        )
    else:
        st.warning("No results found. Try using different keywords or select a module.")

# ============================================
# AI TEST CASE GENERATION
# ============================================
st.write("---")
st.write("## 🤖 AI Test Case Generator")
st.write("Describe a feature and get fresh AI-generated test scenarios in the same style as above.")

feature_description = st.text_area(
    "Describe the feature to test:",
    placeholder="e.g. User can apply a discount code at checkout"
)

if st.button("Generate Test Cases with AI"):
    if not feature_description.strip():
        st.warning("Please describe a feature first.")
    else:
        with st.spinner("Generating test cases..."):
            system_prompt = (
                "You are a senior QA engineer focused on thorough test coverage. Generate test "
                "scenarios in this exact style:\n"
                "MODULE NAME - POSITIVE SCENARIOS\n"
                "- scenario one\n"
                "- scenario two\n\n"
                "MODULE NAME - NEGATIVE SCENARIOS\n"
                "- scenario one\n\n"
                "MODULE NAME - EDGE CASES\n"
                "- scenario one\n\n"
                "Aim for at least 4-5 scenarios per category (Positive, Negative, Edge Cases) to "
                "ensure thorough coverage, including boundary values, validation failures, and "
                "unusual but realistic user behavior. Keep each bullet concise but specific, "
                "starting with 'Verify' where natural. Use the feature name in place of MODULE NAME."
            )
            user_prompt = f"Generate QA test scenarios for this feature: {feature_description}"
            ai_output = call_openai(system_prompt, user_prompt)

        st.session_state["tc_output"] = ai_output
        st.session_state["tc_feature"] = feature_description

if "tc_output" in st.session_state:
    st.write("### Generated Test Scenarios")
    st.code(st.session_state["tc_output"])
    st.download_button(
        "⬇️ Download AI Test Scenarios",
        st.session_state["tc_output"],
        "ai_generated_test_scenarios.txt"
    )
    feedback_buttons("Test Case Generator", st.session_state.get("tc_feature", ""), key_suffix="tc")

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
            system_prompt = (
                "You are a senior QA engineer reviewing a requirement or user story "
                "before it goes into development. Critique it constructively. Cover:\n"
                "1. Ambiguity - any vague or unclear wording\n"
                "2. Missing acceptance criteria - what's not defined\n"
                "3. Untestable language - words that can't be verified objectively\n"
                "4. Edge cases not covered - what scenarios are missing\n"
                "Format your response with clear headers for each section above. "
                "Be specific and constructive, not just critical."
            )
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

ac_format = st.radio(
    "Choose format:",
    ["Given/When/Then (Gherkin)", "Simple Checklist"],
    horizontal=True
)

if st.button("Generate Acceptance Criteria"):
    if not ac_requirement_text.strip():
        st.warning("Please paste a requirement first.")
    else:
        with st.spinner("Generating acceptance criteria..."):
            if ac_format == "Given/When/Then (Gherkin)":
                system_prompt = (
                    "You are a senior business analyst. Given a requirement or user story, "
                    "write clear acceptance criteria in Gherkin format (Given/When/Then). "
                    "Produce at least 3 scenarios covering the main happy path and key variations. "
                    "Format each scenario as:\n"
                    "Scenario: <short title>\n"
                    "Given <context>\n"
                    "When <action>\n"
                    "Then <expected outcome>\n\n"
                    "Separate scenarios with a blank line."
                )
            else:
                system_prompt = (
                    "You are a senior business analyst. Given a requirement or user story, "
                    "write clear acceptance criteria as a simple checklist. "
                    "Each line should be a single, testable, unambiguous criterion starting with "
                    "'The system should...' or 'The user can...'. "
                    "Produce at least 5 checklist items covering the main happy path, validation, and key edge cases."
                )
            user_prompt = f"Write acceptance criteria for this requirement:\n\n{ac_requirement_text}"
            ac_output = call_openai(system_prompt, user_prompt)

        st.session_state["ac_output"] = ac_output
        st.session_state["ac_requirement"] = ac_requirement_text

if "ac_output" in st.session_state:
    st.write("### Generated Acceptance Criteria")
    formatted_output = st.session_state["ac_output"].replace("\nGiven", "  \nGiven").replace("\nWhen", "  \nWhen").replace("\nThen", "  \nThen").replace("\nAnd", "  \nAnd")
    st.markdown(formatted_output)
    st.download_button(
        "⬇️ Download Acceptance Criteria",
        st.session_state["ac_output"],
        "acceptance_criteria.txt"
    )
   feedback_buttons("Acceptance Criteria Generator", st.session_state.get("ac_requirement", ""), key_suffix="ac")

# ============================================
# STRUCTURED OUTPUT: EXCEL EXPORT (AI-POWERED STEPS)
# ============================================
st.write("---")
st.write("## 📊 Export Test Cases to Excel")
st.write("Paste any test scenario text (e.g. from the AI generator above). AI will fill in real Steps, Test Data, and Expected Results for each one, then export to Excel.")

export_text = st.text_area(
    "Paste test scenarios to export:",
    placeholder="Paste AI-generated or existing test scenarios here..."
)

if st.button("Convert to Excel"):
    if not export_text.strip():
        st.warning("Please paste some test scenarios first.")
    else:
        with st.spinner("Generating detailed steps, test data and expected results..."):
            system_prompt = (
                "You are a senior QA engineer with deep test coverage expertise. You will be given "
                "a block of test scenario text, organized under headers like 'MODULE NAME - CATEGORY' "
                "followed by '-' bulleted scenarios. "
                "For each individual bullet scenario, produce a structured, high-quality test case. "
                "Write specific, actionable steps - use concrete field names, button labels, and "
                "exact user actions instead of vague descriptions like 'perform the action'. "
                "Each test case should typically have between 3 and 7 steps depending on what the "
                "scenario actually requires - never pad with filler steps, but never skip steps needed "
                "for someone unfamiliar with the feature to execute the test precisely. "
                "Separately, identify the specific input values used in the test (e.g. sample prices, "
                "usernames, file types, dates) as 'test_data' - if no specific data applies, use 'N/A'. "
                "Additionally, for each module/category group, add 1-2 extra test cases beyond what was "
                "listed if you identify an important coverage gap (e.g. a missing boundary condition, "
                "a missing negative case, or a missing edge case), and mark these with "
                "\"test_scenario\" prefixed by '[AI-added] '. "
                "Return ONLY valid JSON, no markdown, no code fences, no commentary. "
                "Return a JSON array where each item has exactly these fields: "
                "\"module\" (the module name from the header), "
                "\"category\" (the category from the header, e.g. Positive/Negative/Edge Case), "
                "\"test_scenario\" (the original bullet text, or '[AI-added] ...' for new ones), "
                "\"steps\" (a single string with numbered steps separated by newlines, specific and actionable), "
                "\"test_data\" (a single string with the specific input values used, or 'N/A'), "
                "\"expected_result\" (a single string describing the specific, measurable expected outcome)."
            )
            user_prompt = f"Convert this into structured test cases:\n\n{export_text}"
            ai_output = call_openai(system_prompt, user_prompt)

        cleaned = ai_output.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            test_cases = json.loads(cleaned)
            df = pd.DataFrame(test_cases)
            df.insert(0, "Test ID", [f"TC-{i+1:03d}" for i in range(len(df))])
            df = df.rename(columns={
                "module": "Module",
                "category": "Category",
                "test_scenario": "Test Scenario",
                "steps": "Steps",
                "test_data": "Test Data",
                "expected_result": "Expected Result"
            })
            df["Actual Result"] = ""
            df["Status"] = ""
            st.session_state["excel_df"] = df
        except json.JSONDecodeError:
            st.session_state["excel_df"] = None
            st.session_state["excel_raw"] = ai_output

if st.session_state.get("excel_df") is not None:
    df = st.session_state["excel_df"]
    st.write("### Preview")
    st.dataframe(df, use_container_width=True)

    df = df.reset_index(drop=True)   
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Test Cases")
    buffer.seek(0)

    st.download_button(
        "⬇️ Download Excel File",
        buffer,
        "test_cases.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    feedback_buttons("Excel Export", key_suffix="excel")
elif "excel_raw" in st.session_state:
    st.warning("AI response couldn't be parsed into a table. Raw response below:")
    st.code(st.session_state["excel_raw"])

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
