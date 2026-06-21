import time
import requests

BASE_URL = "https://api.fda.gov/drug/event.json"


def search_adverse_events(drug_a: str, drug_b: str) -> dict:
    search_query = (
        f'patient.drug.medicinalproduct:"{drug_a}"'
        f' AND patient.drug.medicinalproduct:"{drug_b}"'
    )

    params = {
        "search": search_query,
        "count": "patient.reaction.reactionmeddrapt.exact",
        "limit": 10,
    }

    try:
        time.sleep(0.5)
        response = requests.get(BASE_URL, params=params, timeout=15)

        if response.status_code in [404, 429]:
            return {"drug_a": drug_a, "drug_b": drug_b, "reactions": []}

        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        reactions = [
            {"reaction": item.get("term"), "count": item.get("count")}
            for item in results
        ]

        return {
            "drug_a": drug_a,
            "drug_b": drug_b,
            "reactions": reactions,
            "source": "OpenFDA",
        }

    except Exception as e:
        return {
            "drug_a": drug_a,
            "drug_b": drug_b,
            "reactions": [],
            "error": str(e),
            "source": "OpenFDA",
        }


if __name__ == "__main__":
    print(search_adverse_events("metformin", "ibuprofen"))