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
    query = query.replace("/", " ").replace("-", " ")   # ✅ FIX UI + checkout cases

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

    # ✅ MODULE MAP (KEPT SAME STRUCTURE)
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
        "checkout": ["checkout", "payment"],   # ✅ FIXED
        "api": ["api"],

        "ui": ["ui", "frontend"],
        "ui non-functional": ["non functional"],
        
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

    # ✅ PRIORITY MATCHES (STRICT)
    if "api security" in query:
        matched_module = "api security"
    elif "data security" in query:
        matched_module = "data security"
    elif "checkout" in query or "payment" in query:
        matched_module = "checkout"
    elif "upload" in query:
        matched_module = "upload"
    elif "download" in query:
        matched_module = "download"
    elif "search" in query:
        matched_module = "search"

    for section in sections:
        section_text = section.lower()
        title = section.strip().split("\n")[0].lower()
        title = title.replace("/", " ").replace("-", " ")   # ✅ FIX titles

        # ✅ SHOW ALL
        if "all" in query:
            results.append(section)
            continue

        if matched_module:

            # ✅ CHECKOUT / PAYMENT FIX
            if matched_module == "checkout":
                if "checkout" in title or "payment" in title:
                    if filter_type:
                        if filter_type in title:
                            results.append(section)
                    else:
                        results.append(section)

            # ✅ UI FIX
            elif matched_module == "ui":
                if "ui" in title or "frontend" in title:
                    if filter_type:
                        if filter_type in title:
                            results.append(section)
                    else:
                        results.append(section)

            elif matched_module == "ui non-functional":
                if "non functional" in title:
                    if filter_type:
                        if filter_type in title:
                            results.append(section)
                    else:
                        results.append(section)

            # ✅ API SECURITY STRICT
            elif matched_module == "api security":
                if "api security" in section_text:
                    if filter_type:
                        if filter_type in section_text:
                            results.append(section)
                    else:
                        results.append(section)

            # ✅ DATA SECURITY STRICT
            elif matched_module == "data security":
                if "data security" in section_text:
                    if filter_type:
                        if filter_type in section_text:
                            results.append(section)
                    else:
                        results.append(section)

            # ✅ GENERAL MATCH
            elif any(word in title for word in module_map[matched_module]):
                if filter_type:
                    if filter_type in title:
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
        st.write("No match found. Try: checkout, ui frontend, api security, etc.")
