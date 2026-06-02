
import streamlit as st

st.title("QA Assistant Chatbot 🤖")

user_input = st.text_input("Ask a QA question:")

if user_input:
    st.write("You asked:", user_input)
