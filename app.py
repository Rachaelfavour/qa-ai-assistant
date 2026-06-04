import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ FIXED SPLIT
sections = re.split(
    r"\n(?=[A-Z ]+ -|===|[A-Z ]+ SCENARIOS|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING|AUTHENTICATION & AUTHORIZATION|SESSION MANAGEMENT|DATA SECURITY|API SECURITY)",
    content
)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Search or ask a QA question:")

if query:
    query = query.lower()
    query = query.replace("/", " ").replace("-", " ")

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

    # ✅ PRIORITY FIXES
    if "api security" in query:
        matched_module = "api security"
    elif "data security" in query:
        matched_module = "data security"
    elif "ui non functional" in query:
        matched_module = "ui non-functional"
    elif "checkout" in query or "payment" in query:
        matched_module = "checkout"

    for section in sections:
        section_text = section.lower()
        title = section.strip().split("\n")[0].lower()
        title = title.replace("/", " ").replace("-", " ")

        # ✅ SHOW ALL
        if "all" in query:
            results.append(section)
            continue

        if matched_module:

            if matched_module == "checkout":
                if "checkout" in title or "payment" in title:
                    results.append(section)

            elif matched_module == "ui":
                if ("ui" in title or "frontend" in title) and "non functional" not in title:
                    results.append(section)

            elif matched_module == "ui non-functional":
                if "non functional" in title:
                    results.append(section)

            elif "xss" in query or "cross site scripting" in query or "cross-site scripting" in query:
                if "xss" in title or "cross site scripting" in title:
                    results.append(section)

            elif matched_module == "session":
                if "session management" in title or "session hijacking" in title:
                    results.append(section)

            elif matched_module == "api security":
                if "api security" in section_text:
                    results.append(section)

            elif matched_module == "data security":
                if "data security" in section_text:
                    results.append(section)

            elif matched_module == "accessibility":
                if "accessibility" in title:
                    results.append(section)

            elif matched_module == "regression":
                if "regression" in title:
                    results.append(section)

            elif matched_module == "database":
                if "database" in title:
                    results.append(section)

            elif matched_module == "performance":
                if "performance" in title:
                    results.append(section)

            elif matched_module == "api":
                if "api" in title and "api security" not in title:
                    results.append(section)

            elif any(word in title for word in module_map[matched_module]):
                results.append(section)

    # ✅ APPLY FILTER
    if filter_type:
        results = [sec for sec in results if filter_type in sec.lower()]

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
        st.write("No match found. Please try different keywords.")
