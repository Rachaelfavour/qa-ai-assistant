import streamlit as st
import re
import json
import pandas as pd
import io
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
# AI TEST CASE GENERATION (STRUCTURED JSON)
# ============================================
st.write("---")
st.write("## 🤖 AI Test Case Generator")
st.write("Describe a feature and get fresh AI-generated test cases with full Steps and Expected Results.")

feature_description = st.text_area(
    "Describe the feature to test:",
    placeholder="e.g. User can schedule a recurring weekly meeting",
    key="feature_input"
)

if st.button("Generate Test Cases with AI"):
    if not feature_description.strip():
        st.warning("Please describe a feature first.")
    else:
        with st.spinner("Generating test cases..."):
            system_prompt = (
                "You are a senior QA engineer. Generate test cases for the given feature. "
                "Return ONLY valid JSON, no markdown formatting, no commentary, no code fences. "
                "Return a JSON array where each item has exactly these fields: "
                "\"module\" (string), \"category\" (one of: Positive, Negative, Edge Case), "
                "\"test_case\" (short title), \"steps\" (array of strings, step-by-step actions), "
                "\"expected_result\" (string). "
                "Generate at least 2 Positive, 2 Negative, and 2 Edge Case test cases."
            )
            user_prompt = f"Generate structured QA test cases for this feature: {feature_description}"
            ai_output = call_openai(system_prompt, user_prompt)

        st.session_state["last_ai_output"] = ai_output

if "last_ai_output" in st.session_state:
    raw = st.session_state["last_ai_output"]
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        test_cases = json.loads(cleaned)
        df = pd.DataFrame(test_cases)
        df["steps"] = df["steps"].apply(lambda s: "\n".join(s) if isinstance(s, list) else s)
        df = df.rename(columns={
            "module": "Module",
            "category": "Category",
            "test_case": "Test Case",
            "steps": "Steps",
            "expected_result": "Expected Result"
        })

        st.write("### Generated Test Cases")
        st.dataframe(df, use_container_width=True)

        # Feedback loop
        st.write("#### Was this output useful?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Useful"):
                st.session_state["feedback_log"] = st.session_state.get("feedback_log", [])
                st.session_state["feedback_log"].append({"feature": feature_description, "rating": "up"})
                st.success("Thanks for the feedback!")
        with col2:
            if st.button("👎 Not useful"):
                st.session_state["feedback_log"] = st.session_state.get("feedback_log", [])
                st.session_state["feedback_log"].append({"feature": feature_description, "rating": "down"})
                st.info("Thanks — noted for improvement.")

        # Excel export
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, sheet_name="Test Cases")
        buffer.seek(0)
        st.download_button(
            "⬇️ Download Excel File",
            buffer,
            "ai_test_cases.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # JSON export
        st.download_button(
            "⬇️ Download JSON File",
            json.dumps(test_cases, indent=2),
            "ai_test_cases.json",
            mime="application/json"
        )

    except json.JSONDecodeError:
        st.warning("Couldn't parse structured output. Showing raw AI response instead:")
        st.code(raw)

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
