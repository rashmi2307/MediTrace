import os
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from models.local_mock import LocalMockModel

class DrugEntry(BaseModel):
    name: str = Field(description="Generic name of the drug, in lowercase. If unknown, use the brand name.")
    dosage: str = Field(description="Dosage of the drug, e.g., 10mg, 500mg")
    frequency: str = Field(description="Frequency of the drug, e.g., twice daily, once daily")

class DrugList(BaseModel):
    drugs: list[DrugEntry] = Field(description="A clean, deduplicated list of drugs with dosages and frequencies")

DRUG_EXTRACTOR_PROMPT = (
    "Extract all medication names and dosages from the following text or image. "
    "Return ONLY a JSON array of objects with keys: name (generic name, lowercase), "
    "dosage (string, e.g. \"10mg\"), frequency (string, e.g. \"twice daily\"). "
    "If the generic name is unknown, use the brand name. Deduplicate. Return nothing else."
)

drug_extractor_agent = LlmAgent(
    name="drug_extractor",
    model=LocalMockModel() if not os.environ.get("USE_REAL_LLM") else "gemini-2.0-flash",
    instruction=DRUG_EXTRACTOR_PROMPT,
    output_schema=DrugList,
    description="Extracts a structured list of drugs, dosages, and frequencies from raw text or prescription images."
)

def extract_drugs_deterministic(user_input: str) -> list[str]:
    import re
    words = re.split(r'[, ]+', user_input)
    extracted = [w.strip().lower() for w in words if len(w) > 4 and w.lower() not in {"this", "that", "image", "uploaded"}]
    return extracted
if __name__ == "__main__":
    import asyncio
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    async def test():
        session_service = InMemorySessionService()
        runner = Runner(agent=drug_extractor_agent, session_service=session_service, app_name="meditrace", auto_create_session=True)
        
        user_text = "I take Lipitor 10mg and metformin 500mg twice daily"
        content = types.Content(role="user", parts=[types.Part(text=user_text)])
        
        print("Running DrugExtractorAgent test...")
        async with runner:
            async for event in runner.run_async(
                user_id="test_user",
                session_id="test_session_1",
                new_message=content
            ):
                if event.content and event.content.parts:
                    text = "".join(p.text or "" for p in event.content.parts)
                    print(text, end="")
        print("\nTest completed.")

    asyncio.run(test())
