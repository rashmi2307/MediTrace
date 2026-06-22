import os
from google.adk.agents import LlmAgent
from models.local_mock import LocalMockModel

REPORT_GENERATOR_PROMPT = (
    "You are a medical report generator. Given a list of medications and a clinical risk assessment, "
    "generate a structured markdown report. "
    "Include exactly the following sections in this order:\n"
    "## Your medications\n"
    "## What looks safe\n"
    "## Watch out for\n"
    "## See a doctor today\n"
    "## Disclaimer\n\n"
    "Under 'Disclaimer', include: 'This report is for information only. It is not medical advice. "
    "Always confirm with your doctor or pharmacist before changing any medication.'"
)

report_generator_agent = LlmAgent(
    name="report_generator",
    model=LocalMockModel() if not os.environ.get("USE_REAL_LLM") else "gemini-2.0-flash",
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

    risks = risk_assessment.get("risks", [])
    if risks:
        safe_list = "No minor interactions found."
        watch_out_lines = []
        see_doctor_lines = []
        
        for r in risks:
            drug_a = r['drug_a'].capitalize()
            drug_b = r['drug_b'].capitalize()
            severity_badge = "[Major Risk]" if r["severity"] == "major" else "[Moderate Risk]"
            
            card = []
            card.append(f"### {drug_a} & {drug_b}")
            card.append(f"**Severity:** {severity_badge}")
            card.append(f"**Source:** {r['source']}")
            card.append(f"**Explanation:** {r['description']}")
            
            top_reactions = r.get('top_reactions', [])
            if top_reactions:
                card.append("**Top reported adverse events:**")
                for reaction in top_reactions:
                    card.append(f"- {reaction}")
            
            card.append(f"**Recommended Action:** {r['action']}")
            card.append("")
            
            card_str = "\n".join(card)
            
            if r["severity"] == "moderate":
                watch_out_lines.append(card_str)
                why_this_matters.append(f"- {drug_a} + {drug_b}: Monitoring is advised to prevent adverse symptoms.")
            elif r["severity"] == "major":
                see_doctor_lines.append(card_str)
                why_this_matters.append(f"- {drug_a} + {drug_b}: This carries severe risks such as bleeding or kidney issues and requires medical oversight.")
        
        if watch_out_lines:
            watch_out = "\n".join(watch_out_lines)
        if see_doctor_lines:
            see_doctor = "\n".join(see_doctor_lines)

    lines.append("## What looks safe")
    lines.append(safe_list)
    lines.append("")
    lines.append("## Watch out for")
    lines.append(watch_out)
    lines.append("")
    lines.append("## See a doctor today")
    lines.append(see_doctor)
    lines.append("")
    
    if why_this_matters:
        lines.append("## Why this matters")
        lines.append("\n".join(why_this_matters))
        lines.append("")
        
    lines.append("## Disclaimer")
    lines.append("This report is for information only. It is not medical advice. Always confirm with your doctor or pharmacist before changing any medication.")
    
    return "\n".join(lines)