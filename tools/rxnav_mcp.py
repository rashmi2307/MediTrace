import requests
from tools import tool

BASE_URL = "https://rxnav.nlm.nih.gov/REST"
_RXCUI_CACHE = {}

@tool
def get_rxcui(drug_name: str) -> str:
    """
    Find RxCUI concept ID for a given drug name.
    """
    key = drug_name.lower().strip()
    if key in _RXCUI_CACHE:
        return _RXCUI_CACHE[key]

    try:
        response = requests.get(f"{BASE_URL}/rxcui.json", params={"name": drug_name}, timeout=15)
        if response.status_code != 200:
            return ""
        data = response.json()
        rxcui = data["idGroup"]["rxnormId"][0]
        _RXCUI_CACHE[key] = rxcui
        return rxcui
    except Exception:
        return ""

@tool
def get_interactions(rxcui: str) -> list:
    """
    Get all interactions for a given RxCUI ID using DrugBank as source.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/interaction/interaction.json",
            params={"rxcui": rxcui, "sources": "DrugBank"},
            timeout=15
        )
        if response.status_code != 200:
            return []
        data = response.json()
        interactions = []
        interaction_type_group = data.get("interactionTypeGroup", [])
        for group in interaction_type_group:
            for interaction_type in group.get("interactionType", []):
                for interaction_pair in interaction_type.get("interactionPair", []):
                    interactions.append({
                        "description": interaction_pair.get("description", ""),
                        "severity": interaction_pair.get("severity", "unknown"),
                        "source": "DrugBank"
                    })
        return sorted(interactions, key=lambda x: x.get("severity", "unknown"))
    except Exception:
        return []

@tool
def get_interaction_pair(rxcui_a: str, rxcui_b: str) -> dict:
    """
    Check if two drugs (by RxCUI) have a known interaction using the list endpoint.
    """
    try:
        # Note: requests handles URL parameter formatting; we also accept manually combined keys.
        response = requests.get(
            f"{BASE_URL}/interaction/list.json",
            params={"rxcuis": f"{rxcui_a}+{rxcui_b}"},
            timeout=15
        )
        if response.status_code != 200:
            return {"has_interaction": False, "interactions": [], "source": "RxNav"}
        
        data = response.json()
        groups = data.get("fullInteractionTypeGroup", [])
        interactions = []
        for group in groups:
            for interaction_type in group.get("fullInteractionType", []):
                for pair in interaction_type.get("interactionPair", []):
                    interactions.append({
                        "description": pair.get("description", ""),
                        "severity": pair.get("severity", "unknown"),
                        "source": pair.get("interactionConcept", [{}])[0].get("sourceConceptItem", {}).get("sourceName", "RxNav")
                    })
        return {
            "has_interaction": len(interactions) > 0,
            "interactions": interactions,
            "source": "RxNav"
        }
    except Exception:
        return {"has_interaction": False, "interactions": [], "source": "RxNav"}