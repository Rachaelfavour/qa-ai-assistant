"""
ai_helper.py
Centralised Groq (OpenAI-compatible) integration for the QA Assistant Chatbot.
"""

import streamlit as st
from openai import OpenAI


def get_client():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("No Groq API key found. Add GROQ_API_KEY to your Streamlit secrets.")
        st.stop()
    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def call_openai(system_prompt: str, user_prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI request failed: {e}"
