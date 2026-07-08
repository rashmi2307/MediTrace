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
    "When the user provides a list of medications, you must: "
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
    import time
    from utils.logger import log_analysis
    import config
    
    start_time = time.time()
    log_extracted = []
    log_interactions = 0
    log_severity = "unknown"
    log_api_failures = 0
    report_status = "failed"
    
    from guardrails.input_guard import check_input
    from guardrails.output_guard import evaluator
    from memory.patient_memory import memory_service
    
    # 1. Input Guardrail
    if config.ENABLE_GUARDRAILS:
        input_check = await check_input(user_input)
        if not input_check.get("is_safe", False):
            log_analysis(user_input, [], 0, "unknown", time.time() - start_time, 0, "rejected")
            return f"Input rejected: {input_check.get('reason', 'Unsafe input detected.')}"
        
    # Determine if we are running deterministically
    use_real_llm = config.USE_REAL_LLM
    
    # 2. Generator Function for Evaluator
    async def generate_report_draft(feedback: str) -> str:
        nonlocal log_extracted, log_interactions, log_severity, log_api_failures
        
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
                try:
                    if get_rxcui(d):
                        valid_drugs.append(d)
                except Exception:
                    log_api_failures += 1
            
            print("valid_drugs:", valid_drugs)
            
            if len(valid_drugs) < 2:
                return "I could not detect at least two valid medications. Please enter medication names such as metformin, ibuprofen, aspirin, or cetirizine."
                
            extracted_drugs = valid_drugs
            log_extracted = extracted_drugs
            
            interaction_results = check_interactions(extracted_drugs)
            log_interactions = len(interaction_results)
            print("interaction_results:", json.dumps(interaction_results, indent=2))
            
            risk_assessment = assess_risks(interaction_results)
            if risk_assessment.get("risks"):
                log_severity = "moderate"
                for r in risk_assessment["risks"]:
                    if r["severity"] == "major":
                        log_severity = "major"
                        break
            else:
                log_severity = "safe"
                
            print("risk_assessment:", json.dumps(risk_assessment, indent=2))
            
            final_report_before_evaluator = generate_report_deterministic(risk_assessment, extracted_drugs)
            print("final_report_before_evaluator:\n", final_report_before_evaluator)
            print("----------------------------")
            
            # Save to memory immediately since we have the true list
            if config.ENABLE_MEMORY:
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
    try:
        if config.ENABLE_EVALUATOR:
            final_report = await evaluator.evaluate_and_retry(generate_report_draft)
            print("evaluator_result passes and returned final report.")
        else:
            final_report = await generate_report_draft(None)
            print("evaluator skipped, returned final report.")
        report_status = "success"
    except Exception as e:
        report_status = "failed"
        raise
    finally:
        # 4. Save to memory if we didn't already
        if use_real_llm and config.ENABLE_MEMORY:
            import re
            extracted = [w.strip().capitalize() for w in re.split(r'[, ]+', user_input) if len(w) > 4 and w.lower() not in {"this", "that"}]
            if not extracted:
                extracted = ["Drug A", "Drug B"]
            memory_service.store_medications(user_id, extracted)
            log_extracted = extracted
            
        execution_time = time.time() - start_time
        log_analysis(
            medications_entered=user_input,
            extracted_medications=log_extracted,
            interaction_count=log_interactions,
            overall_severity=log_severity,
            execution_time=execution_time,
            api_failures=log_api_failures,
            report_status=report_status
        )
    
    return final_report

if __name__ == "__main__":
    import asyncio
    report = asyncio.run(run_meditrace("I take ibuprofen and metformin", "user_123", "session_123"))
    print(report)