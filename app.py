import streamlit as st
import re

# ✅ Load QA data
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ Split sections (handles === headings + normal titles)
sections = re.split(r"\n(?=[A-Z ]+ -|===)", content)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ KEYWORD MAPPING (THIS FIXES PASSWORD RESET)
    keyword_map = {
        "login": ["login"],
        "logout": ["logout"],
        "registration": ["registration"],
        "search": ["search"],
        "upload": ["upload"],
        "download": ["download"],
        "password": ["password reset"],
        "reset": ["password reset"],
        "security": ["sql", "xss", "session", "authentication", "authorization"],
        "xss": ["xss", "cross-site scripting"],
        "sql": ["sql injection"],
        "session": ["session"],
        "api": ["api"],
        "performance": ["performance"],
        "database": ["database"],
        "accessibility": ["accessibility"],
        "regression": ["regression"],
        "ui": ["ui"]
    }

    # ✅ Detect module from full sentence
    matched_group = None

    for key, keywords in keyword_map.items():
        if any(word in query for word in keywords):
            matched_group = key
            break

    for section in sections:
        section_text = section.lower()
        title = section.strip().split("\n")[0].lower()

        # ✅ SHOW EVERYTHING
        if "all" in query:
            results.append(section)
            continue

        # ✅ MATCH MODULE
        if matched_group:
            if any(word in title for word in keyword_map[matched_group]):
                results.append(section)

    # ✅ REMOVE DUPLICATES
    results = list(dict.fromkeys(results))

    # ✅ DISPLAY RESULTS
    if results:
        for sec in results:
            st.text(sec)
            st.write("---")
            download_text += sec + "\n\n"

        st.download_button(
            label="⬇️ Download Test Scenarios",
            data=download_text,
            file_name="qa_test_scenarios.txt",
            mime="text/plain"
        )

    else:
        st.write("No match found. Try: login, password reset, security, search, or type 'all'")
