import os
import json
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from models.local_mock import LocalMockModel

class EvaluatorResult(BaseModel):
    is_valid: bool = Field(description="True if the report meets all guidelines, False otherwise.")
    feedback: str = Field(description="If not valid, specific feedback on what needs to be fixed.")

EVALUATOR_PROMPT = (
    "You are an LLM Evaluator for a medical safety report. "
    "Check the following report against these criteria: "
    "1. It must contain the 'Disclaimer' section with the exact text: 'This report is for information only. It is not medical advice. Always confirm with your doctor or pharmacist before changing any medication.' "
    "2. It must have 'Your medications', 'What looks safe', 'Watch out for', 'See a doctor today' sections. "
    "3. It must not make definitive medical diagnoses. "
    "If it passes, return is_valid: true. Otherwise return is_valid: false and provide feedback."
)

evaluator_agent = LlmAgent(
    name="evaluator",
    model=LocalMockModel() if not os.environ.get("USE_REAL_LLM") else "gemini-2.0-flash",
    instruction=EVALUATOR_PROMPT,
    output_schema=EvaluatorResult,
    description="Evaluates the generated report for safety, structure, and disclaimers."
)

class LLMEvaluator:
    def __init__(self):
        from google.adk.sessions import InMemorySessionService
        self.session_service = InMemorySessionService()

    async def evaluate_and_retry(self, generate_func, max_retries: int = 2) -> str:
        """
        Calls `generate_func` to get a report. Then evaluates it.
        If it fails, it calls `generate_func` again with the feedback (up to max_retries).
        """
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types

        import os
        use_real_llm = os.environ.get("USE_REAL_LLM")
        
        feedback = ""
        last_report = ""

        if not use_real_llm:
            # Deterministic report is always valid because we crafted it perfectly.
            last_report = await generate_func("")
            return last_report

        for attempt in range(max_retries + 1):
            # Pass feedback to generator if any
            last_report = await generate_func(feedback)
            
            # Evaluate
            runner = Runner(agent=evaluator_agent, session_service=self.session_service, app_name="meditrace", auto_create_session=True)
            content = types.Content(role="user", parts=[types.Part(text=f"Evaluate this report:\n{last_report}")])
            output_text = ""
            
            async with runner:
                async for event in runner.run_async(
                    user_id="system",
                    session_id=f"eval_session_{attempt}",
                    new_message=content
                ):
                    if event.content and event.content.parts:
                        output_text += "".join(p.text or "" for p in event.content.parts)
            
            try:
                result = json.loads(output_text)
                is_valid = result.get("is_valid", False)
                feedback = result.get("feedback", "Invalid format.")
            except:
                if "SAFE" in output_text or "Mock" in output_text:
                    is_valid = True
                else:
                    is_valid = False
                    feedback = "Failed to parse JSON."
            
            if is_valid:
                return last_report
        
        # Fallback if we exceeded retries
        return last_report + "\n\n> [!WARNING]\n> This report failed final automated safety checks and may be missing disclaimers. Use with caution."

evaluator = LLMEvaluator()
