import sys
import asyncio
from pathlib import Path
import uuid
import json
from datetime import datetime, timedelta

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.orchestrator import run_meditrace
from memory.patient_memory import memory_service

USER_ID = "demo_user"

# -----------------------------
# Markdown / Card Parser Functions
# -----------------------------
from frontend.parsers import clean_html, parse_markdown_report, parse_interaction_cards, parse_medications

import config

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="💊",
    layout="wide",
)

# -----------------------------
# Theme & Typography CSS Injection
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    /* Global Font Override */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }

    /* Custom CSS variables */
    :root {
        --primary-color: #0f766e;
        --primary-hover: #0d9488;
        --card-bg: var(--secondary-background-color);
        --border-color: rgba(128, 128, 128, 0.15);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        border-right: 1px solid var(--border-color);
    }

    .patient-profile-card {
        background-color: rgba(128, 128, 128, 0.05);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }

    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, rgba(15, 118, 110, 0.1) 0%, rgba(13, 148, 136, 0.05) 100%);
        border-radius: 16px;
        margin-bottom: 30px;
        border: 1px solid rgba(15, 118, 110, 0.15);
    }

    .hero-title {
        font-size: 2.8em;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #0f766e 0%, #0d9488 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.1em;
        opacity: 0.8;
        margin-top: 8px;
        font-weight: 500;
    }

    /* Styled Pills */
    .pill-badge {
        background-color: rgba(15, 118, 110, 0.1);
        color: #0f766e;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9em;
        display: inline-block;
        border: 1px solid rgba(15, 118, 110, 0.2);
    }

    /* Disclaimer Box */
    .disclaimer-box {
        background-color: rgba(239, 68, 68, 0.04);
        border-left: 5px solid #ef4444;
        border-radius: 4px 12px 12px 4px;
        padding: 16px;
        margin-top: 30px;
        border-top: 1px solid rgba(239, 68, 68, 0.1);
        border-right: 1px solid rgba(239, 68, 68, 0.1);
        border-bottom: 1px solid rgba(239, 68, 68, 0.1);
    }

    .disclaimer-title {
        font-weight: 700;
        color: #ef4444;
        font-size: 1.0em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Printable Area Print CSS */
    @media print {
        header, footer, section[data-testid="stSidebar"], .stButton, .stTextArea, .no-print, [data-testid="stHeader"] {
            display: none !important;
        }
        body * {
            visibility: hidden;
        }
        #printable-area, #printable-area * {
            visibility: visible;
        }
        #printable-area {
            position: absolute;
            left: 0;
            top: 0;
            width: 100% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Medication Timeline Logic
# -----------------------------
HISTORY_FILE = ROOT / "memory" / "history.json"

def get_timeline():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def add_timeline_entry(meds_str, risk_level, num_interactions):
    history = get_timeline()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "medications": meds_str,
        "risk_level": risk_level,
        "interactions": num_interactions
    }
    history.insert(0, entry)
    history = history[:10] # Max 10 recent
    
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def format_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        today = datetime.now().date()
        dt_date = dt.date()
        if dt_date == today:
            return "Today"
        elif dt_date == today - timedelta(days=1):
            return "Yesterday"
        else:
            return dt_date.strftime("%b %d, %Y")
    except:
        return "Unknown Date"

st.sidebar.title("Medication Timeline")

timeline = get_timeline()
if not timeline:
    st.sidebar.info("No previous analyses.")
else:
    for entry in timeline:
        date_str = format_date(entry["timestamp"])
        st.sidebar.markdown(f"""
        <div style="background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <div style="font-size: 0.8em; opacity: 0.7; margin-bottom: 4px;">{date_str}</div>
            <div style="font-weight: 600; font-size: 0.95em; margin-bottom: 8px; line-height: 1.4;">{entry['medications']}</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85em; align-items: center;">
                <span>{entry['risk_level']}</span>
                <span style="opacity: 0.7;">{entry['interactions']} interaction{'s' if entry['interactions'] != 1 else ''}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# Theme Selection Overrides
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.write("**Settings**")

theme_choice = st.sidebar.radio("App Theme Override", ["Auto / System", "Light Mode", "Dark Mode"], horizontal=True)

if theme_choice == "Dark Mode":
    st.markdown(
        """
        <style>
        /* Override Streamlit Native Variables */
        :root {
            --background-color: #0E1117 !important;
            --secondary-background-color: #262730 !important;
            --text-color: #FAFAFA !important;
            color-scheme: dark !important;
        }
        /* Force container backgrounds */
        [data-testid="stAppViewContainer"], .stApp {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        [data-testid="stSidebar"] {
            background-color: #262730 !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(14, 17, 23, 0.8) !important;
        }
        /* Typography - explicitly force text color against Streamlit's native Light Mode inheritance */
        .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, 
        label, .stText, .stSidebar p, .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6, .stSidebar li, .stSidebar strong, .stSidebar div, .stSidebar span {
            color: #FAFAFA !important;
        }
        /* Buttons */
        button[kind="secondary"] {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border-color: rgba(250, 250, 250, 0.2) !important;
        }
        button[kind="secondary"] p, button[kind="secondary"] span {
            color: #FAFAFA !important;
        }
        button[kind="primary"] {
            background-color: #0f766e !important;
            color: #FFFFFF !important;
            border-color: #0f766e !important;
        }
        button[kind="primary"] p, button[kind="primary"] span {
            color: #FFFFFF !important;
        }
        /* Form Inputs */
        .stTextArea textarea {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border-color: rgba(250, 250, 250, 0.2) !important;
        }
        /* Revert specific custom colored elements */
        .pill-badge { color: #0f766e !important; }
        .disclaimer-title, .disclaimer-title span { color: #ef4444 !important; }
        /* Update our custom cards */
        :root {
            --card-bg: #262730 !important;
            --border-color: rgba(250, 250, 250, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
elif theme_choice == "Light Mode":
    st.markdown(
        """
        <style>
        /* Override Streamlit Native Variables */
        :root {
            --background-color: #FFFFFF !important;
            --secondary-background-color: #F0F2F6 !important;
            --text-color: #31333F !important;
            color-scheme: light !important;
        }
        /* Force container backgrounds */
        [data-testid="stAppViewContainer"], .stApp {
            background-color: #FFFFFF !important;
            color: #31333F !important;
        }
        [data-testid="stSidebar"] {
            background-color: #F0F2F6 !important;
        }
        [data-testid="stHeader"] {
            background-color: rgba(255, 255, 255, 0.8) !important;
        }
        /* Typography - explicitly force text color against Streamlit's native Dark Mode inheritance */
        .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, 
        label, .stText, .stSidebar p, .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6, .stSidebar li, .stSidebar strong, .stSidebar div, .stSidebar span {
            color: #31333F !important;
        }
        /* Buttons */
        button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #31333F !important;
            border-color: rgba(49, 51, 63, 0.2) !important;
        }
        button[kind="secondary"] p, button[kind="secondary"] span {
            color: #31333F !important;
        }
        button[kind="primary"] {
            background-color: #0f766e !important;
            color: #FFFFFF !important;
            border-color: #0f766e !important;
        }
        button[kind="primary"] p, button[kind="primary"] span {
            color: #FFFFFF !important;
        }
        /* Form Inputs */
        .stTextArea textarea {
            background-color: #FFFFFF !important;
            color: #31333F !important;
            border-color: rgba(49, 51, 63, 0.2) !important;
        }
        /* Revert specific custom colored elements */
        .pill-badge { color: #0f766e !important; }
        .disclaimer-title, .disclaimer-title span { color: #ef4444 !important; }
        /* Update our custom cards */
        :root {
            --card-bg: #FFFFFF !important;
            --border-color: rgba(49, 51, 63, 0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        :root {
            --card-bg: var(--secondary-background-color);
            --border-color: rgba(128, 128, 128, 0.15);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        /* Native Browser Print Fallback */
        @media print {
            section[data-testid="stSidebar"], header[data-testid="stHeader"], .stApp > header, 
            [data-testid="stToolbar"], .stTextArea, button { 
                display: none !important; 
            }
            .stApp, .main, [data-testid="stAppViewContainer"] {
                background-color: white !important;
                color: black !important;
            }
            .interaction-card, .disclaimer-box {
                break-inside: avoid !important;
                page-break-inside: avoid !important;
            }
            hr { display: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Hero Section
# -----------------------------
st.markdown(
    """
    <div class="hero-section">
        <div style="font-size: 3.5em; margin-bottom: 5px;">💊</div>
        <h1 class="hero-title">MediTrace</h1>
        <div class="hero-subtitle">AI-powered Medication Safety Assistant</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Main Application Logic
# -----------------------------
med_input = st.text_area(
    "Enter your medications (separated by commas)",
    placeholder="Example: metformin, ibuprofen, aspirin, cetirizine",
    key="med_input",
    height=120,
)

col_btn, col_actions = st.columns([2, 3])

with col_btn:
    analyze_clicked = st.button("🔍 Analyze Medications", type="primary", use_container_width=True)

with col_actions:
    # Print, Rerun, and Clear History row in standard Streamlit UI
    sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)
    with sub_col1:
        report_data = st.session_state.get("last_report", "")
        pdf_bytes = st.session_state.get("last_pdf_bytes", None)
        
        if config.ENABLE_PDF_EXPORT:
            if report_data:
                if not pdf_bytes:
                    from frontend.pdf_generator import generate_clinical_pdf
                    try:
                        pdf_bytes = generate_clinical_pdf(report_data)
                        st.session_state["last_pdf_bytes"] = pdf_bytes
                    except Exception as e:
                        st.error(f"Failed to generate PDF: {e}")
                
                if pdf_bytes:
                    filename = f"meditrace_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button("⬇️ PDF Report", data=pdf_bytes, file_name=filename, mime="application/pdf", use_container_width=True)
                else:
                    st.button("⬇️ PDF Report", disabled=True, use_container_width=True)
            else:
                st.button("⬇️ PDF Report", disabled=True, use_container_width=True)
    
    with sub_col2:
        if config.ENABLE_MARKDOWN_EXPORT:
            if report_data:
                md_filename = f"meditrace_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                st.download_button("⬇️ Markdown", data=report_data, file_name=md_filename, mime="text/markdown", use_container_width=True)
            else:
                st.button("⬇️ Markdown", disabled=True, use_container_width=True)
            
    with sub_col3:
        rerun_clicked = st.button("🔄 Rerun App", use_container_width=True)
    with sub_col4:
        clear_clicked = st.button("🗑️ Clear Profile", use_container_width=True)

if rerun_clicked:
    st.rerun()

if clear_clicked:
    st.session_state.clear()
    st.success("State cleared.")
    st.rerun()

if analyze_clicked:
    user_query = med_input.strip()

    if not user_query:
        st.error("Please enter at least two medications.")
    else:
        session_id = str(uuid.uuid4())

        # Always clear old report before generating a new one
        st.session_state["last_report"] = None
        st.session_state["last_pdf_bytes"] = None
        st.session_state["last_input"] = user_query
        st.session_state["last_session_id"] = session_id

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

        # Process and save to timeline if successful
        if st.session_state.get("last_report"):
            report = st.session_state["last_report"]
            if not ("I could not detect" in report or "Input rejected" in report):
                sections = parse_markdown_report(report)
                
                major_cards = parse_interaction_cards(sections.get("See a doctor today", ""))
                mod_cards = parse_interaction_cards(sections.get("Watch out for", ""))
                
                num_interactions = len(major_cards) + len(mod_cards)
                
                if major_cards:
                    risk_level = "🔴 Major"
                elif mod_cards:
                    risk_level = "🟡 Moderate"
                else:
                    risk_level = "🟢 Safe"
                    
                meds_checked = user_query
                if "Your medications" in sections:
                    parsed_meds = parse_medications(sections["Your medications"])
                    if parsed_meds:
                        meds_checked = " + ".join(parsed_meds)
                
                add_timeline_entry(meds_checked, risk_level, num_interactions)
                
        st.rerun()

def render_interaction_card(card: dict, severity_level: str):
    if severity_level == "major":
        badge_color = "#ef4444"
        badge_text = "🔴 Major Risk"
    elif severity_level == "moderate":
        badge_color = "#f59e0b"
        badge_text = "🟡 Moderate Risk"
    else:
        badge_color = "#10b981"
        badge_text = "🟢 Safe"
        
    reactions_html = "".join([f"<li>{r}</li>" for r in card["reactions"]])
    reactions_section = f"""
    <div style="margin-top: 10px;">
        <span style="font-weight: 600; font-size: 0.9em; opacity: 0.85;">Top reported adverse events:</span>
        <ul style="margin: 5px 0 0 20px; padding: 0; font-size: 0.95em;">
            {reactions_html}
        </ul>
    </div>
    """ if card["reactions"] else ""

    card_html = f"""
    <div class="interaction-card" style="
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: var(--card-bg);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 12px;">
            <h3 style="margin: 0; font-size: 1.2em; font-weight: 700;">{card["pair"]}</h3>
            <span style="background-color: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}44; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85em;">{badge_text}</span>
        </div>
        <div style="font-size: 0.95em; line-height: 1.55;">
            <div style="margin-bottom: 10px;">
                <span style="font-weight: 600; opacity: 0.85;">Explanation:</span> {card["explanation"]}
            </div>
            {reactions_section}
            <div style="margin-top: 12px; padding: 10px 14px; background-color: {badge_color}11; border-left: 4px solid {badge_color}; border-radius: 0 8px 8px 0;">
                <span style="font-weight: 600; color: {badge_color};">Recommendation:</span> {card["recommendation"]}
            </div>
            <div style="margin-top: 12px; font-size: 0.85em; opacity: 0.7; display: flex; align-items: center; gap: 4px;">
                <span>📂 Evidence Source:</span> <strong>{card["source"]}</strong>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(card_html), unsafe_allow_html=True)


# -----------------------------
# Report Display Render
# -----------------------------
if st.session_state.get("last_report"):
    report = st.session_state["last_report"]
    
    st.markdown("<hr/>", unsafe_allow_html=True)
    
    # Check if report is an extraction warning/error
    if "I could not detect at least two valid medications" in report or "Input rejected" in report:
        st.warning(report)
    else:
        try:
            sections = parse_markdown_report(report)
            
            # Wrap the printable area in a div
            # Wrap the printable area in a container
            report_container = st.container()
            with report_container:
                st.markdown('<span id="pdf-marker" style="display:none;"></span>', unsafe_allow_html=True)

                # Custom Printable Header
                st.markdown(
                    clean_html("""
                    <div style="border-bottom: 2px solid #0f766e; padding-bottom: 10px; margin-bottom: 25px;">
                        <h2 style="margin: 0; color: #0f766e; font-weight: 800;">📋 Medication Safety Report</h2>
                        <span style="font-size: 0.85em; color: grey;">Generated by MediTrace Clinical Safety Agent</span>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

                # 1. Medications pill badges
                if "Your medications" in sections:
                    meds = parse_medications(sections["Your medications"])
                    meds_pills = "".join([f'<span class="pill-badge" style="margin-right: 8px; margin-bottom: 8px;">{m}</span>' for m in meds])
                    st.markdown(
                        clean_html(f"""
                        <div style="margin-bottom: 25px;">
                            <h4 style="margin-top: 0; margin-bottom: 12px; font-weight: 700;">Medications Checked</h4>
                            <div style="display: flex; flex-wrap: wrap;">
                                {meds_pills}
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                # 2. Major Risks (See a doctor today)
                if "See a doctor today" in sections:
                    major_cards = parse_interaction_cards(sections["See a doctor today"])
                    if major_cards:
                        st.markdown('<h4 style="color: #ef4444; font-weight: 700; margin-top: 25px; margin-bottom: 12px;">🔴 Major Risks - Immediate Doctor Visit Required</h4>', unsafe_allow_html=True)
                        for card in major_cards:
                            render_interaction_card(card, "major")

                # 3. Moderate Risks (Watch out for)
                if "Watch out for" in sections:
                    mod_cards = parse_interaction_cards(sections["Watch out for"])
                    if mod_cards:
                        st.markdown('<h4 style="color: #f59e0b; font-weight: 700; margin-top: 25px; margin-bottom: 12px;">🟡 Moderate Risks - Monitoring Advised</h4>', unsafe_allow_html=True)
                        for card in mod_cards:
                            render_interaction_card(card, "moderate")

                # 4. Safe Section (What looks safe)
                if "What looks safe" in sections:
                    safe_text = sections["What looks safe"]
                    if safe_text and safe_text.strip() != "None" and "Everything looks safe" in safe_text:
                        st.markdown(
                            clean_html(f"""
                            <div class="interaction-card" style="border: 1px solid #10b981; border-radius: 12px; padding: 20px; margin-bottom: 20px; background-color: rgba(16, 185, 129, 0.04);">
                                <div style="display: flex; align-items: center; gap: 8px; color: #10b981; font-weight: 700; font-size: 1.1em; margin-bottom: 8px;">
                                    <span>🟢</span> What Looks Safe
                                </div>
                                <div style="font-size: 0.95em; line-height: 1.5;">
                                    {safe_text}
                                </div>
                            </div>
                            """),
                            unsafe_allow_html=True
                        )

                # 5. Why this matters (Context)
                if "Why this matters" in sections:
                    why_text = sections["Why this matters"]
                    if why_text and why_text.strip() != "None":
                        # Convert list to nice layout
                        why_html = ""
                        for item in why_text.split('\n'):
                            item_stripped = item.strip()
                            if item_stripped.startswith('- '):
                                why_html += f"<li style='margin-bottom: 8px;'>{item_stripped[2:]}</li>"

                        if why_html:
                            st.markdown(
                                clean_html(f"""
                                <div style="margin-top: 30px; margin-bottom: 25px;">
                                    <h4 style="margin-top: 0; margin-bottom: 12px; font-weight: 700;">📝 Clinical Summary</h4>
                                    <div style="font-size: 0.95em; line-height: 1.55; background-color: rgba(128, 128, 128, 0.02); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px;">
                                        <ul style="margin: 0; padding-left: 20px;">
                                            {why_html}
                                        </ul>
                                    </div>
                                </div>
                                """),
                                unsafe_allow_html=True
                            )

                # 6. Disclaimer info box
                if "Disclaimer" in sections:
                    disc_text = sections["Disclaimer"]
                else:
                    disc_text = "This report is for information only. It is not medical advice. Always confirm with your doctor or pharmacist before changing any medication."

                st.markdown(
                    clean_html(f"""
                    <div class="disclaimer-box">
                        <div class="disclaimer-title">
                            <span>⚠️</span> Medical Safety Disclaimer
                        </div>
                        <div style="font-size: 0.9em; color: #b91c1c; line-height: 1.5; font-weight: 500;">
                            {disc_text}
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

            
        except Exception as e:
            # Safe Fallback to plain markdown
            st.error("Custom card rendering encountered an error. Showing plain report text.")
            st.markdown(report)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey; font-size: 0.85em;'>"
    "MediTrace Medication Safety Checker &copy; 2026. For educational and Capstone demonstration purposes only."
    "</div>",
    unsafe_allow_html=True,
)