import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ Split into sections properly
sections = re.split(r"\n(?=[A-Z ]+ -|===|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING)", content)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ detect filter
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    # ✅ detect module (MAIN KEYWORDS)
    if "login" in query:
        module = "login"
    elif "logout" in query:
        module = "logout"
    elif "password" in query or "reset" in query:
        module = "password reset"
    elif "registration" in query:
        module = "registration"
    elif "upload" in query:
        module = "upload"
    elif "download" in query:
        module = "download"
    elif "search" in query:
        module = "search"
    elif "security" in query:
        module = "security"
    elif "xss" in query:
        module = "xss"
    elif "sql" in query:
        module = "sql"
    elif "session" in query:
        module = "session"
    elif "all" in query:
        module = "all"
    else:
        module = None

    for section in sections:
        title = section.strip().split("\n")[0].lower()

        # ✅ show all
        if module == "all":
            results.append(section)
            continue

        # ✅ SECURITY FIX (STRICT)
        if module == "security":
            if any(word in title for word in ["sql injection", "xss", "session", "authentication", "authorization"]):
                if filter_type:
                    if filter_type in title:
                        results.append(section)
                else:
                    results.append(section)

        # ✅ INDIVIDUAL SECURITY TYPES
        elif module == "xss":
            if "xss" in title:
                results.append(section)

        elif module == "sql":
            if "sql injection" in title:
                results.append(section)

        elif module == "session":
            if "session" in title:
                results.append(section)

        # ✅ NORMAL MODULES
        elif module:
            if module in title:
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
        st.write("No match found. Try: login, password reset, security, etc.")
