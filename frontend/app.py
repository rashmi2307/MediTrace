import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.orchestrator import run_meditrace


st.set_page_config(
    page_title="MediTrace — Medication Safety Checker",
    page_icon="💊",
    layout="centered",
)

st.title("💊 MediTrace")
st.subheader("Medication Safety Checker")

st.warning(
    "MediTrace is for information only. It is not a substitute for professional medical advice."
)

med_input = st.text_area(
    "Enter your medicines separated by commas",
    placeholder="Example: metformin, ibuprofen",
)

if st.button("Check safety"):
    medications = [
        med.strip().lower()
        for med in med_input.split(",")
        if med.strip()
    ]

    if len(medications) < 2:
        st.error("Please enter at least two medicines.")
    else:
        with st.spinner("Checking interactions and generating report..."):
            report = run_meditrace(medications)

        st.session_state["last_report"] = report
        st.markdown(report)

if "last_report" in st.session_state:
    st.divider()
    st.subheader("Last report")
    st.markdown(st.session_state["last_report"])