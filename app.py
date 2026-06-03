import streamlit as st
import re

# ✅ Load QA data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ Split into sections (your original working method)
sections = re.split(r"\n(?=[A-Z ]+ -|===)", content)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    main_word = query.split()[0]   # ✅ first meaningful keyword

    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].lower()

        # ✅ STRICT MODULE MATCHING

        # Authentication & core modules
        if title.startswith("login") and main_word == "login":
            results.append(section)

        elif title.startswith("logout") and main_word == "logout":
            results.append(section)

        elif title.startswith("registration") and main_word == "registration":
            results.append(section)

        elif title.startswith("search") and main_word == "search":
            results.append(section)

        elif title.startswith("upload") and main_word == "upload":
            results.append(section)

        elif title.startswith("download") and main_word == "download":
            results.append(section)

        # ✅ ✅ SECURITY GROUP (FIXED PROPERLY)
        elif main_word == "security":
            if any(keyword in title for keyword in [
                "sql injection",
                "cross-site scripting",
                "xss",
                "session",
                "authentication",
                "authorization",
                "data security",
                "api security",
                "security testing"
            ]):
                results.append(section)

        # ✅ allow direct keyword access too
        elif main_word in ["xss", "sql", "session", "auth"]:
            if any(main_word in title for keyword in [title]):
                results.append(section)

        # ✅ SHOW ALL
        elif main_word == "all":
            results.append(section)

    # ✅ DISPLAY RESULTS
    if results:
        for sec in results:
            st.text(sec)
            st.write("---")
            download_text += sec + "\n\n"

        # ✅ DOWNLOAD BUTTON
        st.download_button(
            label="⬇️ Download Test Scenarios",
            data=download_text,
            file_name="qa_test_scenarios.txt"
        )
    else:
        st.write("No match found. Try: login, security, search, upload or type 'all'")
``
