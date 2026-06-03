import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# Split sections
sections = re.split(r"\n(?=[A-Z ]+ -|===)", content)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ Keyword mapping (includes password reset fix)
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
        "xss": ["xss"],
        "sql": ["sql"],
        "session": ["session"]
    }

    # ✅ detect filter (positive / negative / edge)
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    # ✅ detect module
    matched_group = None
    for key, keywords in keyword_map.items():
        if any(word in query for word in keywords):
            matched_group = key
            break

    for section in sections:
        title = section.strip().split("\n")[0].lower()

        # ✅ show all
        if "all" in query:
            results.append(section)
            continue

        # ✅ match module
        if matched_group:
            if any(word in title for word in keyword_map[matched_group]):

                # ✅ APPLY FILTER (THIS IS THE FIX)
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
        st.write("No match found. Try: login positive, password reset negative, etc.")
