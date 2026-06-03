import streamlit as st

# ✅ Load your QA data file
with open("qa_data.txt", "r") as f:
    content = f.read()

# ✅ Split sections cleanly
sections = content.strip().split("\n\n")

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    for section in sections:
        section_text = section.lower()

        # ✅ FIXED LOGIC:
        # match keyword ONLY inside section,
        # but prevent random mixing by requiring relevance
        if any(word in section_text for word in query.split()) or "all" in query:

            # ✅ safety filter to avoid unrelated noise
            main_topic = query.split()[0]

            if main_topic in section_text or "all" in query:
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
