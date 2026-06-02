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

user_input = st.text_input("Ask a QA question:")

# Search logic
if user_input:
    user_input = user_input.lower()
    st.write("### Suggested Answer")

    found = False

    for title, data in sections:
        for word in user_input.split():
            if word in title.lower():
                st.write(f"## {title}")
                for item in data:
                    st.write(f"- {item}")
                found = True
                break

    if not found:
        st.write("No match found. Try: login, api, upload, etc.")
