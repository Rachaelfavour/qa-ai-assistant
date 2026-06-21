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
