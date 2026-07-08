import os
from google.adk.agents import LlmAgent
from models.local_mock import LocalMockModel
import config

REPORT_GENERATOR_PROMPT = (
    "You are a medical report generator. Given a list of medications and a clinical risk assessment, "
    "generate a structured markdown report. "
    "Include the following sections:\n"
    "1. '## Your medications' section listing the medications.\n"
    "2. Only the relevant safety/risk sections depending on the severity of the risks:\n"
    "   - If there are major risks, include the '## See a doctor today' section with details.\n"
    "   - If there are moderate risks, include the '## Watch out for' section with details.\n"
    "   - If there are no risks at all, include the '## What looks safe' section stating that everything looks safe.\n"
    "   Do not include any empty or 'None' sections, and do not include the 'What looks safe' section if there are moderate or major risks.\n"
    "3. '## Disclaimer' section with the exact text: 'This report is for information only. It is not medical advice. "
    "Always confirm with your doctor or pharmacist before changing any medication.'"
)

report_generator_agent = LlmAgent(
    name="report_generator",
    model=LocalMockModel() if not config.USE_REAL_LLM else "gemini-2.0-flash",
    instruction=REPORT_GENERATOR_PROMPT,
    description="Generates a structured markdown safety report based on medications and risk assessment."
)

def generate_report_deterministic(risk_assessment: dict, medications: list[str]) -> str:
    lines = []
    lines.append("## Your medications")
    for m in medications:
        lines.append(f"- {m.capitalize()}")
    lines.append("")

    safe_list = "Everything looks safe."
    watch_out = "None"
    see_doctor = "None"
    why_this_matters = []
    watch_out_lines = []
    see_doctor_lines = []

    risks = risk_assessment.get("risks", [])
    if risks:
        safe_list = "No minor interactions found."
        
        for r in risks:
            drug_a = r['drug_a'].capitalize()
            drug_b = r['drug_b'].capitalize()
            severity_badge = "[Major Risk]" if r["severity"] == "major" else "[Moderate Risk]"
            
            card = []
            card.append(f"### {drug_a} & {drug_b}")
            card.append(f"\n**Severity:** {severity_badge}")
            card.append(f"\n**Source:** {r['source']}")
            card.append(f"\n**Explanation:** {r['description']}")
            
            top_reactions = r.get('top_reactions', [])
            if top_reactions:
                card.append("\n**Top reported adverse events:**")
                for reaction in top_reactions:
                    card.append(f"- {reaction}")
            
            card.append(f"\n**Recommended Action:** {r['action']}")
            card.append("")
            
            card_str = "\n".join(card)
            
            if r["severity"] == "moderate":
                watch_out_lines.append(card_str)
            elif r["severity"] == "major":
                see_doctor_lines.append(card_str)
                
        # Generate cohesive physician-style summary
        major_pairs = [f"{r['drug_a'].capitalize()} and {r['drug_b'].capitalize()}" for r in risks if r["severity"] == "major"]
        mod_pairs = [f"{r['drug_a'].capitalize()} and {r['drug_b'].capitalize()}" for r in risks if r["severity"] == "moderate"]
        
        if major_pairs:
            pairs_str = ", ".join(major_pairs)
            summary = (
                f"The concurrent use of {pairs_str} is clinically concerning due to severe adverse events reported in OpenFDA and RxNav. "
                "Available evidence indicates this combination may lead to acute complications requiring medical oversight. "
                "The patient must immediately consult their healthcare provider to evaluate safer pharmacological alternatives."
            )
            why_this_matters.append(summary)
        elif mod_pairs:
            pairs_str = ", ".join(mod_pairs)
            summary = (
                f"The co-administration of {pairs_str} warrants clinical monitoring based on available FDA adverse event reports. "
                "While not strictly contraindicated, this combination can interact to produce undesirable physiological side effects. "
                "The patient should discuss this regimen with a pharmacist or physician to ensure appropriate safety monitoring."
            )
            why_this_matters.append(summary)
            
        if watch_out_lines:
            watch_out = "\n".join(watch_out_lines)
        if see_doctor_lines:
            see_doctor = "\n".join(see_doctor_lines)

    if see_doctor_lines:
        lines.append("## See a doctor today")
        lines.append(see_doctor)
        lines.append("")
    if watch_out_lines:
        lines.append("## Watch out for")
        lines.append(watch_out)
        lines.append("")
    if not see_doctor_lines and not watch_out_lines:
        lines.append("## What looks safe")
        lines.append("Everything looks safe.")
        lines.append("")
    
    if why_this_matters:
        lines.append("## Why this matters")
        lines.append("\n".join(why_this_matters))
        lines.append("")
        
    lines.append("## Disclaimer")
    lines.append("This report is for information only. It is not medical advice. Always confirm with your doctor or pharmacist before changing any medication.")
    
    return "\n".join(lines)
