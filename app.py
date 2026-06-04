import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ FIXED SPLIT (ONLY CHANGE MADE HERE ✅)
sections = re.split(
    r"\n(?=[A-Z ]+ -|===|[A-Z ]+ SCENARIOS|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING|AUTHENTICATION &amp; AUTHORIZATION|SESSION MANAGEMENT|DATA SECURITY|API SECURITY)",
    content
)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ filter type
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    # ✅ FULL MODULE MAP (UNCHANGED ✅)
    module_map = {
        "login": ["login"],
        "logout": ["logout"],
        "password reset": ["password"],
        "registration": ["registration"],

        "vehicle": ["vehicle"],
        "order": ["order"],
        "checkout": ["checkout", "payment"],
        "api": ["api"],

        "ui": ["ui", "frontend"],
        "ui non-functional": ["non-functional"],
        
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

    matched_module = None

    for key, words in module_map.items():
        if any(word in query for word in words):
            matched_module = key
            break

    for section in sections:
        title = section.strip().split("\n")[0].lower()

        # ✅ show all
        if "all" in query:
            results.append(section)
            continue

        if matched_module:
            # ✅ special handling for SECURITY (UNCHANGED ✅)
            if matched_module == "security":
                if any(sec in title for sec in ["sql", "xss", "session", "security"]):
                    if filter_type:
                        if filter_type in title:
                            results.append(section)
                    else:
                        results.append(section)

            else:
                if any(word in title for word in module_map[matched_module]):
                    if filter_type:
                        if filter_type in title:
                            results.append(section)
                    else:
                        results.append(section)

    # ✅ remove duplicates
    results = list(dict.fromkeys(results))

    # ✅ display
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
        st.write("No match found. Try: accessibility, api, database, regression, etc.")
