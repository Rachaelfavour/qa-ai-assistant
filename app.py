import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

# Split sections by === blocks (THIS IS THE KEY FIX)
sections = re.split(r"\n=== ", content)

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

    for section in sections:
        section_text = section.lower()

        # ✅ MATCH ANYWORD INSIDE FULL SECTION (THIS FIXES SECURITY)
        if any(word in section_text for word in query.split()) or "all" in query:

            # ✅ APPLY FILTER (positive/negative/edge)
            if filter_type:
                lines = section.split("\n")
                filtered_lines = []

                keep = False
                for line in lines:
                    if filter_type in line.lower():
                        keep = True

                    if keep:
                        filtered_lines.append(line)

                if filtered_lines:
                    results.append("\n".join(filtered_lines))
            else:
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
        st.write("No match found. Try: security, login, password reset, etc.")
