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

    # ✅ MODULE DETECTION (BASED ON YOUR DATA)
    if "ui non functional" in query:
        module = "ui_non_functional"
    elif "ui" in query or "frontend" in query:
        module = "ui"
    elif "cross site scripting" in query or "xss" in query:
        module = "xss"
    elif "session" in query:
        module = "session"
    elif "accessibility" in query:
        module = "accessibility"
    elif "regression" in query:
        module = "regression"
    elif "database" in query:
        module = "database"
    elif "checkout" in query or "payment" in query:
        module = "checkout"
    elif "api security" in query:
        module = "api_security"
    elif "data security" in query:
        module = "data_security"
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

        # ✅ CHECKOUT
        if module == "checkout":
            if "checkout payment" in title:
                results.append(section)

        # ✅ UI FRONTEND ONLY
        elif module == "ui":
            if "ui frontend" in title:
                results.append(section)

        # ✅ UI NON-FUNCTIONAL ONLY
        elif module == "ui_non_functional":
            if "ui non functional" in title:
                results.append(section)

        # ✅ ✅ XSS FIX (EXACT TITLE)
        elif module == "xss":
            if "cross site scripting" in title:
                results.append(section)

        # ✅ ✅ SESSION FIX (REMOVE LOGOUT)
        elif module == "session":
            if title.startswith("session"):
                results.append(section)

        # ✅ ACCESSIBILITY FIX
        elif module == "accessibility":
            if title.startswith("accessibility"):
                results.append(section)

        # ✅ REGRESSION FIX
        elif module == "regression":
            if title.startswith("regression testing"):
                results.append(section)

        # ✅ DATABASE FIX
        elif module == "database":
            if title.startswith("database testing"):
                results.append(section)

        # ✅ API SECURITY
        elif module == "api_security":
            if "api security" in section_text:
                results.append(section)

        # ✅ DATA SECURITY
        elif module == "data_security":
            if "data security" in section_text:
                results.append(section)

        # ✅ API ONLY
        elif module == "api":
            if "api -" in title:
                results.append(section)

        # ✅ LOGIN
        elif module == "login":
            if title.startswith("login"):
                results.append(section)

        # ✅ LOGOUT
        elif module == "logout":
            if title.startswith("logout"):
                results.append(section)

    # ✅ FILTER APPLY
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
