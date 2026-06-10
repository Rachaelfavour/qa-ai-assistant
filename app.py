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
    # ✅ NORMALIZE QUERY (CRITICAL FIX)
    query = query.lower().replace("-", " ")

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

    # ✅ ✅ STRICT PRIORITY MATCHING (ORDER MATTERS)

    if "ui non functional" in query:
        matched_module = "ui non-functional"

    elif query.strip() in ["ui", "frontend"] or "ui " in query:
        # ✅ prevent override by ui non-functional
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

    # ✅ MODULE MAP
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

# ✅ PROCESS SECTIONS  (INDENTED ✅)
    # ✅ PROCESS SECTIONS
    for section in sections:
        section_text = section.lower().replace("-", " ")
        title = section.strip().split("\n")[0].lower().replace("-", " ")

        # ✅ SHOW ALL
        if "all" in query:
            results.append(section)
            continue

        if matched_module:
            keywords = module_map.get(matched_module, [])

            if any(word in title for word in keywords):

                # ✅ FIX ONLY PROBLEM MODULES
                if matched_module == "accessibility" and "accessibility" not in title:
                    continue

                if matched_module == "regression" and "regression" not in title:
                    continue

                if filter_type:
                    if filter_type in title or filter_type in section_text:
                        results.append(section)
                else:
                    results.append(section)

    # ✅ REMOVE DUPLICATES
    results = list(dict.fromkeys(results))

    # ✅ DISPLAY
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
        st.write("No match found. Try: ui, ui non-functional, regression, xss")
