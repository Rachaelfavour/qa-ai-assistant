import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ SAME SPLIT (UNCHANGED)
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

    # ✅ FILTER
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    # ✅ MODULE DETECTION (STRICT)
    if "ui non functional" in query:
        module = "ui non-functional"
    elif "api security" in query:
        module = "api security"
    elif "data security" in query:
        module = "data security"
    elif "checkout" in query or "payment" in query:
        module = "checkout"
    elif "cross site scripting" in query or "xss" in query:
        module = "xss"
    elif "session" in query:
        module = "session"
    elif "ui" in query or "frontend" in query:
        module = "ui"
    elif "accessibility" in query:
        module = "accessibility"
    elif "regression" in query:
        module = "regression"
    elif "database" in query:
        module = "database"
    elif "performance" in query:
        module = "performance"
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
            if "checkout" in title or "payment" in title:
                results.append(section)

        # ✅ UI FUNCTIONAL ONLY
        elif module == "ui":
            if ("ui frontend" in title or "ui" in title) and "non functional" not in title:
                results.append(section)

        # ✅ UI NON-FUNCTIONAL ONLY
        elif module == "ui non-functional":
            if title.startswith("ui non functional"):
                results.append(section)

        # ✅ ✅ XSS STRICT
        elif module == "xss":
            if "cross site scripting" in title or "(xss)" in title:
                results.append(section)

        # ✅ ✅ SESSION STRICT (NO LOGOUT)
        elif module == "session":
            if title.startswith("session"):
                results.append(section)

        # ✅ ACCESSIBILITY STRICT
        elif module == "accessibility":
            if title.startswith("accessibility"):
                results.append(section)

        # ✅ REGRESSION STRICT
        elif module == "regression":
            if title.startswith("regression"):
                results.append(section)

        # ✅ DATABASE STRICT
        elif module == "database":
            if title.startswith("database"):
                results.append(section)

        # ✅ API SECURITY STRICT
        elif module == "api security":
            if "api security" in section_text:
                results.append(section)

        # ✅ DATA SECURITY STRICT
        elif module == "data security":
            if "data security" in section_text:
                results.append(section)

        # ✅ API ONLY (NO SECURITY)
        elif module == "api":
            if "api" in title and "security" not in title:
                results.append(section)

        # ✅ GENERAL
        elif module in title:
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
