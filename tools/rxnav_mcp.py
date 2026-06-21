import requests

BASE_URL = "https://rxnav.nlm.nih.gov/REST"
_RXCUI_CACHE = {}


def get_rxcui(drug_name: str):
    key = drug_name.lower().strip()

    if key in _RXCUI_CACHE:
        return _RXCUI_CACHE[key]

    response = requests.get(f"{BASE_URL}/rxcui.json", params={"name": drug_name}, timeout=15)

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        rxcui = data["idGroup"]["rxnormId"][0]
        _RXCUI_CACHE[key] = rxcui
        return rxcui
    except Exception:
        return None


def get_interaction_pair(rxcui_a: str, rxcui_b: str) -> dict:
    response = requests.get(
        f"{BASE_URL}/interaction/list.json",
        params={"rxcuis": f"{rxcui_a}+{rxcui_b}"},
        timeout=15,
    )

    if response.status_code != 200:
        return {"has_interaction": False, "interactions": [], "source": "RxNav"}

    data = response.json()
    groups = data.get("fullInteractionTypeGroup", [])

    interactions = []

    for group in groups:
        for interaction_type in group.get("fullInteractionType", []):
            for pair in interaction_type.get("interactionPair", []):
                interactions.append(
                    {
                        "description": pair.get("description", ""),
                        "severity": pair.get("severity", "unknown"),
                        "source": pair.get("interactionConcept", [{}])[0]
                        .get("sourceConceptItem", {})
                        .get("sourceName", "RxNav"),
                    }
                )

    return {
        "has_interaction": len(interactions) > 0,
        "interactions": interactions,
        "source": "RxNav",
    }


def check_drug_pair(drug_a: str, drug_b: str) -> dict:
    rxcui_a = get_rxcui(drug_a)
    rxcui_b = get_rxcui(drug_b)

    if not rxcui_a or not rxcui_b:
        return {
            "drug_a": drug_a,
            "drug_b": drug_b,
            "has_interaction": False,
            "reason": "Could not find RxCUI for one or both drugs",
            "source": "RxNav",
        }

    result = get_interaction_pair(rxcui_a, rxcui_b)

    return {
        "drug_a": drug_a,
        "drug_b": drug_b,
        "rxcui_a": rxcui_a,
        "rxcui_b": rxcui_b,
        **result,
    }


if __name__ == "__main__":
    print("metformin:", get_rxcui("metformin"))
    print("ibuprofen:", get_rxcui("ibuprofen"))
    print(check_drug_pair("metformin", "ibuprofen"))