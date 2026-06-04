import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ SPLIT SECTIONS
sections = re.split(
    r"\n(?=[A-Z \-]+ -|===|[A-Z \-]+ SCENARIOS|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING|AUTHENTICATION & AUTHORIZATION|SESSION MANAGEMENT|DATA SECURITY|API SECURITY)",
    content
)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Search or ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ FILTER TYPE
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    matched_module = None

    # ✅ ✅ PRIORITY MATCHING (MOST IMPORTANT FIX)
    if "ui non-functional" in query:
        matched_module = "ui non-functional"
    elif "data security" in query:
        matched_module = "data security"
    elif "api security" in query:
        matched_module = "api security"
    elif "cross-site scripting" in query or "cross site scripting" in query or "xss" in query:
        matched_module = "cross site scripting"
    elif "regression" in query:
        matched_module = "regression"
    elif "accessibility" in query:
        matched_module = "accessibility"
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
    elif "security" in query:
        matched_module = "security"
    elif "session" in query:
        matched_module = "session"
    elif "authentication" in query or "authorization" in query:
        matched_module = "authentication"

    # ✅ MODULE MAP
    module_map = {
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

        "ui": ["ui", "frontend"],
        "ui non-functional": ["ui non functional"],

        "cross site scripting": [
            "cross site scripting",
            "cross-site scripting",
            "xss"
        ],

        "accessibility": ["accessibility"],
        "regression": ["regression"],
        "performance": ["performance"],
        "database": ["database"],

        "security": ["security"],
        "data security": ["data security"],
        "api security": ["api security"],
        "session": ["session"],
        "authentication": ["authentication", "authorization"]
    }

    # ✅ PROCESS SECTIONS
    for section in sections:
        section_text = section.lower().replace("-", " ")
        title = section.strip().split("\n")[0].lower().replace("-", " ")

        # ✅ SHOW ALL
        if "all" in query:
            results.append(section)
            continue

        if matched_module:

            # ✅ STRICT MATCH
            if any(word in title for word in module_map.get(matched_module, [])):

                if filter_type:
                    if filter_type in title:
                        results.append(section)
                else:
                    results.append(section)

            # ✅ FALLBACK FOR SECURITY
            elif matched_module in ["data security", "api security"]:
                if matched_module in section_text:
                    if filter_type:
                        if filter_type in section_text:
                            results.append(section)
                    else:
                        results.append(section)

    # ✅ REMOVE DUPLICATES
    results = list(dict.fromkeys(results))

    # ✅ DISPLAY RESULTS
    if results:
        for sec in results:
            st.text(sec)
            st.write("---")
            download_text += sec + "\n\n"

        st.download_button(
            "⬇️ Download Test Scenarios",
            download_text,
            "qa_test_scenarios.txt"
        )
    else:
        st.write("No match found. Try: ui non-functional, xss, regression, login")
