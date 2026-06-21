from agents.interaction_checker import check_interactions
from agents.risk_assessor import assess_risks
from agents.report_generator import generate_report


def run_meditrace(medications: list[str]) -> str:
    interactions = check_interactions(medications)
    risks = assess_risks(interactions)
    report = generate_report(medications, risks)
    return report


if __name__ == "__main__":
    meds = ["metformin", "ibuprofen"]
    print(run_meditrace(meds))