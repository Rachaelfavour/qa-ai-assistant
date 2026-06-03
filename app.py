import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# Split into sections
sections = re.split(r"\n(?=[A-Z ]+ -|===)", content)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ keyword groups (clean + safe)
    keyword_map = {
        "login": ["login"],
        "logout": ["logout"],
        "registration": ["registration"],
        "search": ["search"],
        "upload": ["upload"],
        "download": ["download"],
        "security": ["sql", "xss", "session", "authentication", "authorization", "security"],
        "xss": ["xss"],
        "sql": ["sql"],
        "session": ["session"]
    }

    # ✅ detect module from full sentence (no restriction)
    matched_group = None
    for key, words in keyword_map.items():
        if any(word in query for word in words):
            matched_group = key
            break

    # ✅ detect filter
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].lower()

        # ✅ show all
        if "all" in query:
            results.append(section)
            continue

        # ✅ module filtering
        if matched_group:
            if any(word in title for word in keyword_map[matched_group]):

                # ✅ apply positive/negative filter if present
                if filter_type:
                    if filter_type in title:
                        results.append(section)
                else:
                    results.append(section)

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
        st.write("No match found. Try: login, security, search, upload or type 'all'")
