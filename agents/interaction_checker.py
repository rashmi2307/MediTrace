import os
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

from tools.rxnav_mcp import get_interaction_pair
from tools.openfda_mcp import search_adverse_events
from tools.search_mcp import web_search_tool
from models.local_mock import LocalMockModel
import config

class InteractionResult(BaseModel):
    drug_a: str
    drug_b: str
    has_interaction: bool
    rxnav: dict = Field(default_factory=dict)
    openfda: dict = Field(default_factory=dict)
    source: str

class InteractionList(BaseModel):
    interactions: list[InteractionResult]

INTERACTION_CHECKER_PROMPT = (
    "You are a medical interaction checker. You will be provided with a list of drug names. "
    "For EVERY possible pairwise combination of drugs in the list, you must check for interactions. "
    "First, use the get_interaction_pair tool to check RxNav. "
    "Then, use the search_adverse_events tool to check OpenFDA. "
    "Merge the results. If no structured data is found, fallback to web_search_tool. "
    "Return a structured list of interactions."
)

interaction_checker_agent = LlmAgent(
    name="interaction_checker",
    model=LocalMockModel() if not config.USE_REAL_LLM else "gemini-2.0-flash",
    instruction=INTERACTION_CHECKER_PROMPT,
    output_schema=InteractionList,
    tools=[get_interaction_pair, search_adverse_events, web_search_tool],
    description="Checks for drug-drug interactions pairwise using RxNav, OpenFDA, and Web Search."
)

def check_interactions(drug_names: list[str]) -> list[dict]:
    import itertools
    results = []
    pairs = list(itertools.combinations(drug_names, 2))
    for a, b in pairs:
        rxnav_result = get_interaction_pair(a, b)
        fda_result = search_adverse_events(a, b)
        
        interaction = {
            "drug_a": a,
            "drug_b": b,
            "has_interaction": rxnav_result.get("has_interaction", False) or len(fda_result.get("reactions", [])) > 0,
            "rxnav": rxnav_result,
            "openfda": fda_result,
            "source": "Deterministic Pipeline"
        }
        results.append(interaction)
    return results