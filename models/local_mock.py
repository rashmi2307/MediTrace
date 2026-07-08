import json
import logging
from typing import AsyncGenerator
from google.genai import types
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

class LocalMockModel(BaseLlm):
    """A local mock model to bypass Vertex AI billing for testing."""
    model: str = "mock-model"

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        # Log the request for debugging
        prompt = ""
        for content in llm_request.contents:
            for part in content.parts:
                if part.text:
                    prompt += part.text + "\n"

        prompt += str(llm_request)

        logging.info(f"Mocking response for prompt: {prompt}")

        # Basic router based on prompt content
        response_text = ""
        import re
        
        # Try to extract words that might be drug names. We know the prompt has the user input text.
        # We'll just extract all alphabetic words longer than 4 chars and pick the first two that aren't common words.
        words = re.findall(r'\b[a-zA-Z]{4,}\b', prompt.lower())
        stop_words = {'evaluate', 'this', 'report', 'your', 'medications', 'what', 'looks', 'safe', 'watch', 'doctor', 'today', 'disclaimer', 'information', 'only', 'medical', 'advice', 'always', 'confirm', 'with', 'pharmacist', 'before', 'changing', 'any', 'medication', 'orchestrate', 'extract', 'evaluate', 'system', 'prompt', 'instructions', 'you', 'are', 'json'}
        
        extracted_drugs = []
        for w in words:
            if w not in stop_words and w not in extracted_drugs:
                extracted_drugs.append(w)
                
        # Fallback if none found
        if not extracted_drugs:
            extracted_drugs = ["drug_a", "drug_b"]

        drug_1 = extracted_drugs[0].capitalize() if len(extracted_drugs) > 0 else "Drug A"
        drug_2 = extracted_drugs[1].capitalize() if len(extracted_drugs) > 1 else "Drug B"

        if "guardrail" in prompt.lower() or "is_safe" in prompt.lower():
            response_text = json.dumps({"is_safe": True, "reason": "Passed local mock"})
        elif "evaluator" in prompt.lower() or "cites_source" in prompt.lower() or "evaluate" in prompt.lower():
            response_text = json.dumps({
                "is_valid": True,
                "feedback": "Report looks good.",
                "cites_source": 1,
                "no_diagnosis": 1,
                "recommends_doctor": 1,
                "plain_language": 1,
                "overall_pass": True
            })
        elif "report" in prompt.lower() or "markdown" in prompt.lower() or "orchestrator" in prompt.lower():
            response_text = f"## Your medications\n- {drug_1}\n- {drug_2}\n\n## What looks safe\nEverything looks safe.\n\n## Disclaimer\nThis report is for information only. It is not medical advice. Always confirm with your doctor or pharmacist before changing any medication."
        elif "extract" in prompt.lower() or ("json" in prompt.lower() and "dosage" in prompt.lower()):
            response_text = json.dumps({
                "drugs": [
                    {"name": drug_1, "dosage": "500mg", "frequency": "twice daily"},
                    {"name": drug_2, "dosage": "200mg", "frequency": "as needed"}
                ]
            })
        else:
            response_text = json.dumps({"is_safe": True, "is_valid": True, "reason": "Default pass", "feedback": "Looks okay"})

        # Simulate a small delay
        import asyncio
        await asyncio.sleep(0.5)

        # In case we need to yield multiple chunks, for now just one
        response = LlmResponse(
            content=types.Content(role='model', parts=[types.Part(text=response_text)]),
            partial=False,
            turn_complete=True
        )
        yield response
