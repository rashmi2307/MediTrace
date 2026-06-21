def assess_risks(interactions: list[dict]) -> dict:
    assessed = []

    for item in interactions:
        drug_a = item["drug_a"]
        drug_b = item["drug_b"]

        rxnav_has = item.get("rxnav", {}).get("has_interaction", False)
        fda_reactions = item.get("openfda", {}).get("reactions", [])

        severity = "minor"
        score = 1
        description = "No major structured interaction found."

        if rxnav_has:
            severity = "moderate"
            score = 2
            description = item["rxnav"]["interactions"][0].get(
                "description", "RxNav reports a possible interaction."
            )

        if fda_reactions:
            top_reaction = fda_reactions[0]["reaction"]
            top_count = fda_reactions[0]["count"]

            severity = "moderate"
            score = max(score, 2)
            description = (
                f"OpenFDA reports adverse events for this combination. "
                f"Top reported event: {top_reaction} ({top_count} reports)."
            )

            kidney_terms = ["KIDNEY", "RENAL"]
            if any(term in top_reaction.upper() for term in kidney_terms):
                severity = "major"
                score = 3

        assessed.append(
            {
                "drug_a": drug_a,
                "drug_b": drug_b,
                "severity": severity,
                "score": score,
                "description": description,
                "source": item.get("source", "RxNav + OpenFDA"),
            }
        )

    assessed.sort(key=lambda x: x["score"], reverse=True)

    return {
        "requires_immediate_doctor_visit": any(
            item["score"] >= 3 for item in assessed
        ),
        "risks": assessed,
    }


if __name__ == "__main__":
    from agents.interaction_checker import check_interactions

    interactions = check_interactions(["metformin", "ibuprofen"])
    print(assess_risks(interactions))