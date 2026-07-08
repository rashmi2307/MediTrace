import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _parse_bool(value: str, default: bool = True) -> bool:
    if value is None:
        return default
    return str(value).lower() in ("true", "1", "t", "yes", "y")

# Feature Flags
USE_REAL_LLM = _parse_bool(os.getenv("USE_REAL_LLM"), False)
ENABLE_MEMORY = _parse_bool(os.getenv("ENABLE_MEMORY"), True)
ENABLE_GUARDRAILS = _parse_bool(os.getenv("ENABLE_GUARDRAILS"), True)
ENABLE_EVALUATOR = _parse_bool(os.getenv("ENABLE_EVALUATOR"), True)
ENABLE_PDF_EXPORT = _parse_bool(os.getenv("ENABLE_PDF_EXPORT"), True)
ENABLE_MARKDOWN_EXPORT = _parse_bool(os.getenv("ENABLE_MARKDOWN_EXPORT"), True)

# App Settings
APP_TITLE = os.getenv("APP_TITLE", "MediTrace \u2014 Medication Safety Checker")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
