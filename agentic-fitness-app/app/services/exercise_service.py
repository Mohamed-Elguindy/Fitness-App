import json
from pathlib import Path
from typing import List, Dict, Optional

class ExerciseService:
    def __init__(self):
        self.app_root = Path(__file__).resolve().parent.parent.parent
        self.data_path = self.app_root / "data" / "exercises.json"
        self.exercises = self._load_data()

    def _load_data(self) -> List[Dict]:
        if not self.data_path.exists():
            return []
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_all_exercises(self) -> List[Dict]:
        """Return the complete list of exercises."""
        return self.exercises

    def get_by_muscle(self, target_muscle: str) -> List[Dict]:
        """Filter exercises by exact primary or secondary muscle."""
        target = target_muscle.lower()
        results = []
        for ex in self.exercises:
            primary = ex.get("primary_muscle", "").lower()
            secondary = [m.lower() for m in ex.get("secondary_muscles", [])]
            if target == primary or target in secondary:
                results.append(ex)
        return results

    def get_by_equipment(self, equipment: str) -> List[Dict]:
        """Filter exercises by required equipment."""
        target = equipment.lower()
        return [ex for ex in self.exercises if ex.get("equipment", "").lower() == target]

    def get_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Filter exercises by difficulty level."""
        target = difficulty.lower()
        return [ex for ex in self.exercises if ex.get("difficulty", "").lower() == target]

    def get_filtered_exercises(self, muscle: Optional[str] = None, equipment: Optional[str] = None, difficulty: Optional[str] = None) -> List[Dict]:
        """Combined strict filtering for the LLM tool."""
        results = self.exercises
        
        if muscle:
            target = muscle.lower()
            results = [
                ex for ex in results 
                if target == ex.get("primary_muscle", "").lower() or target in [m.lower() for m in ex.get("secondary_muscles", [])]
            ]
            
        if equipment:
            eq = equipment.lower()
            if eq == "home":
                results = [ex for ex in results if ex.get("equipment", "").lower() in ["dumbbell", "bodyweight"]]
            elif eq == "gym":
                pass
            else:
                results = [ex for ex in results if ex.get("equipment", "").lower() == eq]
            
        if difficulty:
            results = [ex for ex in results if ex.get("difficulty", "").lower() == difficulty.lower()]
            
        return results
