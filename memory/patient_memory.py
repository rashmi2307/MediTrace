class PatientMemoryService:
    def __init__(self):
        # user_id -> list of medications from previous sessions
        self._history = {}

    def get_medication_history(self, user_id: str) -> list[str]:
        """Retrieve previous medication list for a given user."""
        return self._history.get(user_id, [])

    def store_medications(self, user_id: str, medications: list[str]):
        """Store the current medication list as history for the next session."""
        self._history[user_id] = list(medications)

    def compare_medications(self, user_id: str, current_meds: list[str]) -> dict:
        """
        Compare current medications with the history.
        Returns a dictionary with added, removed, and unchanged medications.
        """
        previous_meds = self.get_medication_history(user_id)
        
        prev_set = set(m.lower() for m in previous_meds)
        curr_set = set(m.lower() for m in current_meds)
        
        added = list(curr_set - prev_set)
        removed = list(prev_set - curr_set)
        unchanged = list(curr_set & prev_set)
        
        return {
            "previous": previous_meds,
            "current": current_meds,
            "added": added,
            "removed": removed,
            "unchanged": unchanged
        }

# Global instance for the local app
memory_service = PatientMemoryService()
