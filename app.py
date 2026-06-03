import streamlit as st

# Load file
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ Split by sections
sections = content.strip().split("\n\n")

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower().split()   # split words
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].lower()

        # ✅ STRICT matching: only match TITLE
        if any(word in title for word in query) or "all" in query:
            results.append(section)

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
        st.write("No match found. Try: login, logout, search, security or type 'all'")
