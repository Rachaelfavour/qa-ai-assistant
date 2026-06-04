import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ KEEP YOUR SPLIT
sections = re.split(
    r"\n(?=[A-Z ]+ -|===|[A-Z ]+ SCENARIOS|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING|AUTHENTICATION & AUTHORIZATION|SESSION MANAGEMENT|DATA SECURITY|API SECURITY)",
    content
)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Search or ask a QA question:")

if query:
    query = query.lower().replace("/", " ").replace("-", " ")

    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ FILTER
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    # ✅ MODULE DETECTION
    if "ui non functional" in query:
        module = "ui non functional"
    elif "ui" in query or "frontend" in query:
        module = "ui"
    elif "cross site scripting" in query or "xss" in query:
        module = "cross site scripting"
    elif "session" in query:
        module = "session"
    elif "accessibility" in query:
        module = "accessibility"
    elif "regression" in query:
        module = "regression"
    elif "database" in query:
        module = "database"
    elif "checkout" in query or "payment" in query:
        module = "checkout payment"
    elif "api security" in query:
        module = "api security"
    elif "data security" in query:
        module = "data security"
    elif "api" in query:
        module = "api"
    elif "login" in query:
        module = "login"
    elif "logout" in query:
        module = "logout"
    else:
        module = None

    for section in sections:
        section_text = section.lower()
        title = section.strip().split("\n")[0].lower()
        title = title.replace("/", " ").replace("-", " ")

        if not module:
            continue

        if module in title:

            # ✅ FIX: remove logout from session
            if module == "session" and "logout" in title:
                continue

            # ✅ FIX: UI separation
            if module == "ui" and "non functional" in title:
                continue
            if module == "ui non functional" and "non functional" not in title:
                continue

            # ✅ FIX: accessibility strict
            if module == "accessibility" and not title.startswith("accessibility"):
                continue

            # ✅ FIX: regression strict
            if module == "regression" and not title.startswith("regression"):
                continue

            # ✅ FIX: database strict
            if module == "database" and not title.startswith("database"):
                continue

            # ✅ FIX: XSS match
            if module == "cross site scripting":
                if "cross site scripting" not in title and "xss" not in title:
                    continue

            results.append(section)

    # ✅ FILTER
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
        st.write("No match found.")
