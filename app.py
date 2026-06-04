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

    # ✅ MODULE MAP (ONLY CHANGE: checkout fixed ✅)
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
        "checkout": ["checkout / payment"],  # ✅ FIXED HERE
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

    # ✅ PRIORITY MATCHES (ONLY ADDED CHECKOUT FIX ✅)
    if "data security" in query:
        matched_module = "data security"
    elif "api security" in query:
        matched_module = "api security"
    elif "search" in query:
        matched_module = "search"
    elif "upload" in query:
        matched_module = "upload"
    elif "download" in query:
        matched_module = "download"
    elif "checkout" in query or "payment" in query:   # ✅ FIXED HERE
        matched_module = "checkout"

    for section in sections:
        section_text = section.lower()
        title = section.strip().split("\n")[0].lower()

        # ✅ SHOW ALL
        if "all" in query:
            results.append(section)
            continue

        if matched_module:

            # ✅ STRICT TITLE MATCH
            if any(word in title for word in module_map[matched_module]):

                if filter_type:
                    if filter_type in title:
                        results.append(section)
                else:
                    results.append(section)

            # ✅ SAFE FALLBACK (UNCHANGED)
            elif matched_module in ["data security", "api security"]:
                if matched_module in section_text:
                    if filter_type:
                        if filter_type in section_text:
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
        st.write("No match found. Try: checkout, payment, login, etc.")
