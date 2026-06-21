"""
ai_helper.py
Centralised OpenAI integration for the QA Assistant Chatbot.

Keeps all AI calls in one place so app.py stays clean and the
prompts/logic are easy to test and reuse across features:
- test case generation
- requirement analysis ("challenge my requirement")
"""

import streamlit as st
from openai import OpenAI


def get_client():
    """
    Returns an OpenAI client using the API key stored in Streamlit secrets.
    Looking for a key called OPENAI_API_KEY in .streamlit/secrets.toml
    (locally) or in the app's Secrets settings (Streamlit Community Cloud).
    """
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "No OpenAI API key found. Add OPENAI_API_KEY to your "
            "Streamlit secrets to enable AI features."
        )
        st.stop()
    return OpenAI(api_key=api_key)


def call_openai(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Generic helper to call the OpenAI chat completion API.
    Returns the raw text response, or an error message string on failure.
    """
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI request failed: {e}"
