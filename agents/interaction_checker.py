from itertools import combinations

from tools.rxnav_mcp import check_drug_pair
from tools.openfda_mcp import search_adverse_events


def check_interactions(drug_names: list[str]) -> list[dict]:
    results = []

    for drug_a, drug_b in combinations(drug_names, 2):
        rxnav_result = check_drug_pair(drug_a, drug_b)
        fda_result = search_adverse_events(drug_a, drug_b)

        has_rxnav = rxnav_result.get("has_interaction", False)
        has_fda = len(fda_result.get("reactions", [])) > 0

        result = {
            "drug_a": drug_a,
            "drug_b": drug_b,
            "has_interaction": has_rxnav or has_fda,
            "rxnav": rxnav_result,
            "openfda": fda_result,
            "source": "RxNav + OpenFDA",
        }

        results.append(result)

    return results


if __name__ == "__main__":
    test_drugs = ["metformin", "ibuprofen"]
    output = check_interactions(test_drugs)

    for item in output:
        print(item)