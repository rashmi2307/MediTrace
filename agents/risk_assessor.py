import os
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from models.local_mock import LocalMockModel

class RiskAssessmentEntry(BaseModel):
    drug_a: str
    drug_b: str
    severity: str = Field(description="minor, moderate, or major")
    score: int = Field(description="Risk score from 1 to 4")
    description: str = Field(description="Description of the risk")
    source: str

class RiskAssessmentList(BaseModel):
    requires_immediate_doctor_visit: bool
    risks: list[RiskAssessmentEntry] = Field(description="Only moderate and major risks. Filter out minor severity.")

RISK_ASSESSOR_PROMPT = (
    "You are a medical risk assessor. Given a structured list of drug interactions, "
    "assess the clinical risk. Assign a severity (minor, moderate, major) and a score (1-4). "
    "Filter out minor severity. Keep only moderate and major. "
    "If any score is >= 3, set requires_immediate_doctor_visit to true. "
    "Consider comorbidity indicators if provided."
)

risk_assessor_agent = LlmAgent(
    name="risk_assessor",
    model=LocalMockModel() if not os.environ.get("USE_REAL_LLM") else "gemini-2.0-flash",
    instruction=RISK_ASSESSOR_PROMPT,
    output_schema=RiskAssessmentList,
    description="Assesses clinical risks based on drug interactions, scoring 1-4, filtering out minor risks."
)

SERIOUS_REACTION_KEYWORDS = {
    "bleeding", "haemorrhage", "hemorrhage", "kidney", "renal", 
    "liver", "hepatic", "anaphylaxis", "respiratory failure", 
    "death", "stroke", "myocardial infarction"
}

def assess_risks(interactions: list[dict]) -> dict:
    requires_doctor = False
    risks = []
    
    for inter in interactions:
        severity = "minor"
        score = 1
        desc = []
        action = "Monitor for any unusual symptoms."
        top_reactions = []

        drug_a = inter["drug_a"].lower()
        drug_b = inter["drug_b"].lower()

        rx_source = False
        fda_source = False

        # Process RxNav
        if inter.get("rxnav", {}).get("has_interaction"):
            rx_source = True
            rx_sev = inter["rxnav"].get("severity", "minor").lower()
            
            # 1. Use RxNav/DrugBank severity if available
            if rx_sev == "contraindicated":
                severity = "major"
                score = max(score, 4)
                requires_doctor = True
                action = "Please consult your doctor immediately."
                desc.append("RxNav reported contraindicated severity.")
            elif rx_sev == "major" or rx_sev == "high":
                severity = "major"
                score = max(score, 3)
                requires_doctor = True
                action = "Please consult your doctor immediately."
                desc.append("RxNav reported major severity.")
            elif rx_sev == "moderate":
                severity = "moderate"
                score = max(score, 2)
                action = "Discuss this combination with your pharmacist or doctor."
                desc.append("RxNav reported moderate severity.")
            else:
                desc.append("RxNav reported minor/low severity.")

        # Process OpenFDA
        reactions = inter.get("openfda", {}).get("reactions", [])
        if reactions:
            fda_source = True
            top_reactions = [r.get("reaction", "").title() for r in reactions[:3]]
            
            serious_keywords_found = []
            max_reaction_count = 0
            
            for r in reactions:
                term = r.get("reaction", "").lower()
                count = r.get("count", 0)
                if count > max_reaction_count:
                    max_reaction_count = count
                    
                for kw in SERIOUS_REACTION_KEYWORDS:
                    if kw in term and kw not in serious_keywords_found:
                        serious_keywords_found.append(kw)
                        
            if serious_keywords_found:
                # If serious keywords appear and event counts are high, classify as major.
                if max_reaction_count > 500:
                    severity = "major"
                    score = max(score, 3)
                    requires_doctor = True
                    action = "Please consult your doctor due to potential severe risks."
                    desc.append(f"OpenFDA serious reaction keyword detected: {serious_keywords_found[0]}.")
                else:
                    severity = "moderate" if score < 3 else severity
                    score = max(score, 2)
                    desc.append(f"OpenFDA serious reaction keyword detected: {serious_keywords_found[0]} (low frequency).")
            else:
                if score < 2:
                    severity = "moderate"
                    score = max(score, 2)
                    action = "Monitor for adverse effects."
                desc.append("OpenFDA reports exist but causation is not proven.")

        if score >= 2:
            sources = []
            if rx_source: sources.append("RxNav")
            if fda_source: sources.append("OpenFDA")
            
            risks.append({
                "drug_a": inter["drug_a"],
                "drug_b": inter["drug_b"],
                "severity": severity,
                "score": score,
                "description": " ".join(desc),
                "action": action,
                "source": " & ".join(sources) if sources else "OpenFDA/RxNav",
                "top_reactions": top_reactions
            })

    # Sort descending by score
    risks.sort(key=lambda x: x["score"], reverse=True)

    return {
        "requires_immediate_doctor_visit": requires_doctor,
        "risks": risks
    }