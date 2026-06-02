import streamlit as st

# Read data
with open("qa_data.txt", "r") as f:
    lines = f.readlines()

# Build sections
sections = []
current_section = ""
section_data = []

for line in lines:
    clean_line = line.strip()

    if clean_line.isupper():
        if current_section and section_data:
            sections.append((current_section, section_data))
        current_section = clean_line
        section_data = []
    else:
        if clean_line != "":
            section_data.append(clean_line)

if current_section and section_data:
    sections.append((current_section, section_data))

# UI
st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Ask a QA question:")

if query:
    query = query.lower()
    st.write("### Suggested Test Scenarios")

    results = []

    # ✅ SMART match (not strict)
    for title, data in sections:
        if query in title.lower() or any(word in title.lower() for word in query.split()):
            results.append((title, data))

    # ✅ SHOW ALL
    if "all" in query:
        results = sections

    # ✅ DISPLAY
    if results:
        for title, data in results:
            st.write(f"## {title}")

            for i, item in enumerate(data, start=1):
                st.write(f"{i}. {item}")   # ✅ numbered steps

            st.write("---")
    else:
        st.write("No match found. Try: login, registration, api, or type 'all'")
