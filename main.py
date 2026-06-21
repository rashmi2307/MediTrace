from agents.orchestrator import run_meditrace


def main():
    print("MediTrace — Medication Safety Checker")
    print("Enter medicines separated by commas.")
    print("Example: metformin, ibuprofen")
    print()

    user_input = input("Medicines: ")

    medications = [
        med.strip().lower()
        for med in user_input.split(",")
        if med.strip()
    ]

    if len(medications) < 2:
        print("Please enter at least two medicines.")
        return

    report = run_meditrace(medications)
    print()
    print(report)


if __name__ == "__main__":
    main()