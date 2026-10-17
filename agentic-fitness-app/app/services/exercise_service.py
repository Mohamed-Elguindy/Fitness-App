import json
from pathlib import Path
from typing import List, Dict, Optional

class ExerciseService:
    def __init__(self):
        self.app_root = Path(__file__).resolve().parent.parent.parent
        self.data_path = self.app_root / "data" / "exercises.json"
        self.exercises = self._load_data()

    # --- Public API (The Headlines) ---

    def get_filtered_exercises(
        self, 
        muscle: Optional[str] = None, 
        equipment: Optional[str] = None, 
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """Combined filtering for exercises by muscle, equipment, and difficulty."""
        results = self.exercises

        if muscle:
            results = self._filter_by_muscle(results, muscle)
        if equipment:
            results = self._filter_by_equipment(results, equipment)
        if difficulty:
            results = self._filter_by_difficulty(results, difficulty)

        return results

    def get_all_exercises(self) -> List[Dict]:
        """Return the complete list of exercises."""
        return self.exercises

    def get_by_muscle(self, target_muscle: str) -> List[Dict]:
        """Filter exercises by exact primary or secondary muscle."""
        return self._filter_by_muscle(self.exercises, target_muscle)

    def get_by_equipment(self, equipment: str) -> List[Dict]:
        """Filter exercises by required equipment."""
        return self._filter_by_equipment(self.exercises, equipment)

    def get_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Filter exercises by difficulty level."""
        return self._filter_by_difficulty(self.exercises, difficulty)

    # --- Filter Helpers (Stepdown Order) ---

    def _filter_by_muscle(self, exercises: List[Dict], target_muscle: str) -> List[Dict]:
        target = target_muscle.lower()
        return [
            exercise for exercise in exercises
            if target == exercise.get("primary_muscle", "").lower()
            or target in [secondary.lower() for secondary in exercise.get("secondary_muscles", [])]
        ]

    def _filter_by_equipment(self, exercises: List[Dict], equipment: str) -> List[Dict]:
        target = equipment.lower()
        if target == "home":
            allowed_equipment = {"dumbbell", "bodyweight"}
            return [exercise for exercise in exercises if exercise.get("equipment", "").lower() in allowed_equipment]
        if target == "gym":
            return exercises
        return [exercise for exercise in exercises if exercise.get("equipment", "").lower() == target]

    def _filter_by_difficulty(self, exercises: List[Dict], difficulty: str) -> List[Dict]:
        target = difficulty.lower()
        return [exercise for exercise in exercises if exercise.get("difficulty", "").lower() == target]

    # --- Data Loading ---

    def _load_data(self) -> List[Dict]:
        if not self.data_path.exists():
            return []

        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)
