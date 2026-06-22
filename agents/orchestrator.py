import os
import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from models.local_mock import LocalMockModel
from agents.drug_extractor import drug_extractor_agent
from agents.interaction_checker import interaction_checker_agent
from agents.risk_assessor import risk_assessor_agent
from agents.report_generator import report_generator_agent

ORCHESTRATOR_PROMPT = (
    "You are the main orchestrator for the MediTrace safety system. "
    "When the user provides a list of medications (or a prescription image), you must: "
    "1. Delegate to drug_extractor to get a structured list. "
    "2. Pass that list to interaction_checker. "
    "3. Pass the interactions to risk_assessor. "
    "4. Pass the final risks and medications to report_generator to generate a markdown report. "
    "Return the final markdown report to the user."
)

orchestrator_agent = LlmAgent(
    name="orchestrator",
    model=LocalMockModel() if not os.environ.get("USE_REAL_LLM") else "gemini-2.0-flash",
    instruction=ORCHESTRATOR_PROMPT,
    sub_agents=[drug_extractor_agent, interaction_checker_agent, risk_assessor_agent, report_generator_agent],
    description="Orchestrates the MediTrace system by coordinating extraction, interaction checking, risk assessment, and report generation."
)

# Shared session service for testing locally without redis
_session_service = InMemorySessionService()

async def run_meditrace(user_input: str, user_id: str, session_id: str) -> str:
    from guardrails.input_guard import check_input
    from guardrails.output_guard import evaluator
    from memory.patient_memory import memory_service
    import os
    
    # 1. Input Guardrail
    input_check = await check_input(user_input)
    if not input_check.get("is_safe", False):
        return f"Input rejected: {input_check.get('reason', 'Unsafe input detected.')}"
        
    # Determine if we are running deterministically
    use_real_llm = os.environ.get("USE_REAL_LLM")
    
    # 2. Generator Function for Evaluator
    async def generate_report_draft(feedback: str) -> str:
        if not use_real_llm:
            from agents.drug_extractor import extract_drugs_deterministic
            from agents.interaction_checker import check_interactions
            from agents.risk_assessor import assess_risks
            from agents.report_generator import generate_report_deterministic
            import json
            
            from tools.rxnav_mcp import get_rxcui
            
            print("--- DEBUG LOCAL PIPELINE ---")
            extracted_drugs = extract_drugs_deterministic(user_input)
            print("extracted_drugs before validation:", extracted_drugs)
            
            valid_drugs = []
            for d in extracted_drugs:
                if get_rxcui(d):
                    valid_drugs.append(d)
            
            print("valid_drugs:", valid_drugs)
            
            if len(valid_drugs) < 2:
                return "I could not detect at least two valid medications. Please enter medication names such as metformin, ibuprofen, aspirin, or cetirizine."
                
            extracted_drugs = valid_drugs
            
            interaction_results = check_interactions(extracted_drugs)
            print("interaction_results:", json.dumps(interaction_results, indent=2))
            
            risk_assessment = assess_risks(interaction_results)
            print("risk_assessment:", json.dumps(risk_assessment, indent=2))
            
            final_report_before_evaluator = generate_report_deterministic(risk_assessment, extracted_drugs)
            print("final_report_before_evaluator:\n", final_report_before_evaluator)
            print("----------------------------")
            
            # Save to memory immediately since we have the true list
            memory_service.store_medications(user_id, extracted_drugs)
            
            return final_report_before_evaluator
            
        else:
            runner = Runner(
                agent=orchestrator_agent, 
                session_service=_session_service, 
                app_name="meditrace", 
                auto_create_session=True
            )
            
            prompt = user_input
            if feedback:
                prompt += f"\n\nPrevious attempt failed evaluation. Feedback: {feedback}"
                
            content = types.Content(role="user", parts=[types.Part(text=prompt)])
            output_text = ""
            
            async with runner:
                async for event in runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=content
                ):
                    if event.content and event.content.parts:
                        output_text += "".join(p.text or "" for p in event.content.parts)
            return output_text
        
    # 3. Output Guardrail (Evaluate and Retry)
    final_report = await evaluator.evaluate_and_retry(generate_report_draft)
    print("evaluator_result passes and returned final report.")
    
    # 4. Save to memory if we didn't already
    if use_real_llm:
        import re
        extracted = [w.strip().capitalize() for w in re.split(r'[, ]+', user_input) if len(w) > 4 and w.lower() not in {"this", "that", "image", "uploaded"}]
        if not extracted:
            extracted = ["Drug A", "Drug B"]
        memory_service.store_medications(user_id, extracted)
    
    return final_report

if __name__ == "__main__":
    import asyncio
    report = asyncio.run(run_meditrace("I take ibuprofen and metformin", "user_123", "session_123"))
    print(report)