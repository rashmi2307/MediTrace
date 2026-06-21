import time
import requests
from tools import tool

BASE_URL = "https://api.fda.gov/drug/event.json"

@tool
def search_adverse_events(drug_a: str, drug_b: str) -> dict:
    """
    Query OpenFDA for reported adverse events when drug_a and drug_b are taken together.
    """
    # Wait 0.5s to stay within rate limits (240 requests/min)
    time.sleep(0.5)

    search_query = f"patient.drug.medicinalproduct:{drug_a} AND patient.drug.medicinalproduct:{drug_b}"
    params = {
        "search": search_query,
        "count": "patient.reaction.reactionmeddrapt.exact",
        "limit": 10
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        
        # Handle 404 and 429 gracefully
        if response.status_code in [404, 429]:
            return {
                "drug_a": drug_a,
                "drug_b": drug_b,
                "reactions": [],
                "source": "OpenFDA"
            }
            
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
            "source": "OpenFDA"
        }
    except Exception as e:
        # Gracefully handle other exceptions by returning an empty list
        return {
            "drug_a": drug_a,
            "drug_b": drug_b,
            "reactions": [],
            "error": str(e),
            "source": "OpenFDA"
        }