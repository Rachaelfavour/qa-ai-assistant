import streamlit as st
import re
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
                "You are a senior QA engineer. Generate test scenarios in this exact style:\n"
                "MODULE NAME - POSITIVE SCENARIOS\n"
                "- scenario one\n"
                "- scenario two\n\n"
                "MODULE NAME - NEGATIVE SCENARIOS\n"
                "- scenario one\n\n"
                "MODULE NAME - EDGE CASES\n"
                "- scenario one\n\n"
                "Keep each bullet concise, starting with 'Verify' where natural. "
                "Use the feature name in place of MODULE NAME."
            )
            user_prompt = f"Generate QA test scenarios for this feature: {feature_description}"
            ai_output = call_openai(system_prompt, user_prompt)

        st.write("### Generated Test Scenarios")
        st.code(ai_output)
        st.download_button(
            "⬇️ Download AI Test Scenarios",
            ai_output,
            "ai_generated_test_scenarios.txt"
        )
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

        st.write("### Requirement Analysis")
        st.write(analysis_output)

# ============================================
# STRUCTURED OUTPUT: EXCEL EXPORT
# ============================================
import pandas as pd
import io

def parse_test_cases_to_dataframe(raw_text):
    """Convert AI-generated test case text into a structured table."""
    rows = []
    current_module = ""
    current_category = ""
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            rows.append({
                "Module": current_module,
                "Category": current_category,
                "Test Scenario": line.lstrip("- ").strip()
            })
        elif " - " in line:
            parts = line.split(" - ", 1)
            current_module = parts[0].strip()
            current_category = parts[1].strip()
        else:
            current_module = line.strip()
            current_category = ""
    return pd.DataFrame(rows)

st.write("---")
st.write("## 📊 Export Test Cases to Excel")
st.write("Paste any test scenario text (e.g. from the AI generator above) to convert it into a structured Excel file.")

export_text = st.text_area(
    "Paste test scenarios to export:",
    placeholder="Paste AI-generated or existing test scenarios here..."
)

if st.button("Convert to Excel"):
    if not export_text.strip():
        st.warning("Please paste some test scenarios first.")
    else:
        df = parse_test_cases_to_dataframe(export_text)
        if df.empty:
            st.warning("Couldn't detect any test scenarios in that text. Make sure lines start with '-'.")
        else:
            st.write("### Preview")
            st.dataframe(df)

            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, sheet_name="Test Cases")
            buffer.seek(0)

            st.download_button(
                "⬇️ Download Excel File",
                buffer,
                "test_cases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
