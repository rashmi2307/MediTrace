def generate_report(medications: list[str], risk_assessment: dict) -> str:
    risks = risk_assessment.get("risks", [])

    safe_items = []
    watch_items = []
    doctor_items = []

    for risk in risks:
        pair = f"{risk['drug_a']} + {risk['drug_b']}"
        text = f"- **{pair}**: {risk['description']} Source: {risk['source']}."

        if risk["severity"] == "major":
            doctor_items.append(text)
        elif risk["severity"] == "moderate":
            watch_items.append(text)
        else:
            safe_items.append(text)

    report = "## Your medications\n"
    for med in medications:
        report += f"- {med}\n"

    report += "\n## What looks safe\n"
    report += "\n".join(safe_items) if safe_items else "No clearly safe interaction pairs were found in this check."

    report += "\n\n## Watch out for\n"
    report += "\n".join(watch_items) if watch_items else "No moderate interactions were found."

    report += "\n\n## See a doctor today\n"
    report += "\n".join(doctor_items) if doctor_items else "No major interactions were found."

    report += (
        "\n\n## Disclaimer\n"
        "This report is for information only. It is not medical advice. "
        "Always confirm with your doctor or pharmacist before changing any medication."
    )

    return report


if __name__ == "__main__":
    from agents.interaction_checker import check_interactions
    from agents.risk_assessor import assess_risks

    meds = ["metformin", "ibuprofen"]
    interactions = check_interactions(meds)
    risks = assess_risks(interactions)
    print(generate_report(meds, risks))