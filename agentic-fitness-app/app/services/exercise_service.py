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
        for exercise in self.exercises:
            primary_muscle = exercise.get("primary_muscle", "").lower()
            secondary_muscles = [muscle.lower() for muscle in exercise.get("secondary_muscles", [])]
            if target == primary_muscle or target in secondary_muscles:
                results.append(exercise)
        return results

    def get_by_equipment(self, equipment: str) -> List[Dict]:
        """Filter exercises by required equipment."""
        target = equipment.lower()
        return [exercise for exercise in self.exercises if exercise.get("equipment", "").lower() == target]

    def get_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Filter exercises by difficulty level."""
        target = difficulty.lower()
        return [exercise for exercise in self.exercises if exercise.get("difficulty", "").lower() == target]

    def get_filtered_exercises(self, muscle: Optional[str] = None, equipment: Optional[str] = None, difficulty: Optional[str] = None) -> List[Dict]:
        """Combined strict filtering for the LLM tool."""
        results = self.exercises
        
        if muscle:
            target = muscle.lower()
            results = [
                exercise for exercise in results 
                if target == exercise.get("primary_muscle", "").lower() or target in [muscle.lower() for muscle in exercise.get("secondary_muscles", [])]
            ]
            
        if equipment:
            target_equipment = equipment.lower()
            if target_equipment == "home":
                results = [exercise for exercise in results if exercise.get("equipment", "").lower() in ["dumbbell", "bodyweight"]]
            elif target_equipment == "gym":
                pass
            else:
                results = [exercise for exercise in results if exercise.get("equipment", "").lower() == target_equipment]
            
        if difficulty:
            results = [exercise for exercise in results if exercise.get("difficulty", "").lower() == difficulty.lower()]
            
        return results
