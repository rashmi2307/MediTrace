import sys
import asyncio
from pathlib import Path
import uuid

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.orchestrator import run_meditrace
from memory.patient_memory import memory_service


USER_ID = "demo_user"


st.set_page_config(
    page_title="MediTrace — Medication Safety Checker",
    page_icon="💊",
    layout="wide",
)


# -----------------------------
# Sidebar: Patient Profile
# -----------------------------
st.sidebar.title("Patient Profile")

try:
    history = memory_service.get_medication_history(USER_ID)
except Exception:
    history = []

if history:
    st.sidebar.write("**Past Medications:**")
    for med in history:
        st.sidebar.write(f"- {med}")
else:
    st.sidebar.write("No medication history found.")

st.sidebar.write("**Known Allergies:** None documented")
st.sidebar.write("**Conditions:** None documented")


# -----------------------------
# Main App
# -----------------------------
st.title("💊 MediTrace")
st.subheader("Medication Safety Checker")

med_input = st.text_area(
    "Enter your medicines separated by commas",
    placeholder="Example: metformin, ibuprofen",
    key="med_input",
)


if st.button("Check safety"):
    user_query = med_input.strip()

    if not user_query:
        st.error("Please enter at least two medicines.")
    else:
        session_id = str(uuid.uuid4())

        # Always clear old report before generating a new one
        st.session_state["last_report"] = None
        st.session_state["last_input"] = user_query
        st.session_state["last_session_id"] = session_id

        st.caption(f"DEBUG input sent: {user_query}")
        st.caption(f"DEBUG session id: {session_id}")

        status_placeholder = st.empty()
        status_placeholder.info("⏳ Extracting medications...")

        try:
            with st.spinner("Checking interactions and generating your report..."):
                report = asyncio.run(
                    run_meditrace(
                        user_query,
                        USER_ID,
                        session_id,
                    )
                )

            status_placeholder.empty()
            st.session_state["last_report"] = report

        except Exception as e:
            status_placeholder.empty()
            st.error("Something went wrong while generating the report.")
            st.exception(e)


if st.session_state.get("last_report"):
    st.markdown(st.session_state["last_report"])


st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey;'>"
    "MediTrace is for information only. Not a substitute for professional medical advice."
    "</div>",
    unsafe_allow_html=True,
)