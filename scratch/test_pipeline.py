import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.orchestrator import run_meditrace

async def test_input(user_input):
    print(f"\n==========================================")
    print(f"Testing input: '{user_input}'")
    print(f"==========================================")
    try:
        report = await run_meditrace(user_input, "test_user_123", "test_session_123")
        print("\n--- GENERATED REPORT ---")
        print(report)
        print("------------------------")
    except Exception as e:
        print("Pipeline failed:", e)

async def main():
    inputs = [
        "aspirin",
        "warfarin",
        "aspirin, warfarin",
        "warfarin, ibuprofen"
    ]
    for inp in inputs:
        await test_input(inp)

asyncio.run(main())
