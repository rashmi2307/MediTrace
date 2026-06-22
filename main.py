import asyncio
import uuid
from agents.orchestrator import run_meditrace


async def main():
    print("MediTrace — Medication Safety Checker")
    print("Enter medicines separated by commas.")
    print("Example: metformin, ibuprofen")
    print()

    user_input = input("Medicines: ")

    if not user_input.strip():
        print("Please enter some medicines.")
        return

    print("\nChecking interactions and generating report...\n")
    session_id = str(uuid.uuid4())
    report = await run_meditrace(user_input, "cli_user", session_id)
    print()
    print(report)


if __name__ == "__main__":
    asyncio.run(main())