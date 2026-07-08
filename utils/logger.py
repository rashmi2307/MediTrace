import json
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "analysis.jsonl")

def log_analysis(
    medications_entered: str,
    extracted_medications: list[str],
    interaction_count: int,
    overall_severity: str,
    execution_time: float,
    api_failures: int,
    report_status: str
):
    """Logs the analysis to a JSONL file without PII."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
        
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "medications_entered": medications_entered,
        "extracted_medications": extracted_medications,
        "interaction_count": interaction_count,
        "overall_severity": overall_severity,
        "execution_time": round(execution_time, 3),
        "api_failures": api_failures,
        "report_status": report_status
    }
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Failed to write log: {e}")
