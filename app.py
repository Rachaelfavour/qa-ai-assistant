import streamlit as st

# Load file
with open("qa_data.txt", "r") as f:
    content = f.read()

sections = content.strip().split("\n\n")

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query_words = query.lower().split()
    main_topic = query_words[0]  # ✅ ONLY FIRST WORD (STRICT)

    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].lower()

        # ✅ STRICT MATCH: ONLY based on main keyword
        if main_topic in title or main_topic == "all":
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
        st.write("No match found. Try: login, logout, security, search or type 'all'")
