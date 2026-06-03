import streamlit as st
import re

# Load file
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ Split into logical sections using headings
sections = re.split(r"\n(?=[A-Z ]+ -)", content)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].lower()

        # ✅ STRICT match on MAIN keyword (login only matches LOGIN sections)
        if title.startswith("login") and "login" in query:
            results.append(section)
        elif title.startswith("logout") and "logout" in query:
            results.append(section)
        elif title.startswith("registration") and "registration" in query:
            results.append(section)
        elif title.startswith("search") and "search" in query:
            results.append(section)
        elif title.startswith("upload") and "upload" in query:
            results.append(section)
        elif title.startswith("download") and "download" in query:
            results.append(section)
        elif "all" in query:
            results.append(section)

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
        st.write("No match found. Try: login, logout, registration, search or type 'all'")
