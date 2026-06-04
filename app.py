import streamlit as st
import re

# Load data
with open("qa_data.txt", "r") as f:
    content = f.read()

sections = re.split(
    r"\n(?=[A-Z ]+ -|===|[A-Z ]+ SCENARIOS|SQL INJECTION|CROSS-SITE SCRIPTING|SESSION HIJACKING|AUTHENTICATION & AUTHORIZATION|SESSION MANAGEMENT|DATA SECURITY|API SECURITY)",
    content
)

st.title("QA Assistant Chatbot 🤖")

query = st.text_input("Search or ask a QA question:")

if query:
    query = query.lower().replace("/", " ").replace("-", " ")

    st.write("### Suggested Test Scenarios")

    results = []
    download_text = ""

    # ✅ FILTER
    filter_type = None
    if "positive" in query:
        filter_type = "positive"
    elif "negative" in query:
        filter_type = "negative"
    elif "edge" in query:
        filter_type = "edge"

    # ✅ LOOP
    for section in sections:
        section_text = section.lower()

        # ✅ GET TITLE
        raw_title = section.strip().split("\n")[0]
        title = raw_title.lower().replace("/", " ").replace("-", " ")

        # ✅ EXTRACT MAIN MODULE (VERY IMPORTANT FIX)
        main_module = title.split(" - ")[0].strip()

        # ✅ MATCH BASED ON YOUR FILE STRUCTURE
        if query in title or query in section_text:

            # ✅ FIX 1: REMOVE LOGOUT FROM SESSION SEARCH
            if "session" in query:
                if main_module == "logout":
                    continue

            # ✅ FIX 2: UI FRONTEND vs NON-FUNCTIONAL
            if "ui frontend" in query or "ui" in query:
                if "non functional" in title:
                    continue

            if "ui non functional" in query:
                if "non functional" not in title:
                    continue

            # ✅ FIX 3: CROSS-SITE SCRIPTING
            if "cross site scripting" in query or "xss" in query:
                if "cross site scripting" not in title:
                    continue

            # ✅ FIX 4: ACCESSIBILITY STRICT
            if "accessibility" in query:
                if not main_module.startswith("accessibility"):
                    continue

            # ✅ FIX 5: REGRESSION STRICT
            if "regression" in query:
                if not main_module.startswith("regression"):
                    continue

            # ✅ FIX 6: DATABASE STRICT
            if "database" in query:
                if not main_module.startswith("database"):
                    continue

            results.append(section)

    # ✅ FILTER TYPE
    if filter_type:
        results = [sec for sec in results if filter_type in sec.lower()]

    # ✅ REMOVE DUPLICATES
    results = list(dict.fromkeys(results))

    # ✅ OUTPUT
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
        st.write("No match found.")
