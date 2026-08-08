import json
from pathlib import Path
from enum import Enum
from typing import Optional, Dict

class Goal(str, Enum):
    BULK = "bulk"
    CUT = "cut"
    MAINTENANCE = "maintenance"
    STRENGTH = "strength"
    HYPERTROPHY = "hypertrophy"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class DietPreference(str, Enum):
    BALANCED = "balanced"
    LOW_CARB = "low_carb"
    KETO = "keto"

class CalculatorService:
    def __init__(self):
        # Load autonomous constants from the RAG extraction script
        app_root = Path(__file__).resolve().parent.parent.parent
        constants_path = app_root / "data" / "science_constants.json"
        
        with open(constants_path, "r", encoding="utf-8") as f:
            self.constants = json.load(f)

        self.ACTIVITY_MULTIPLIERS = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHT: 1.375,
            ActivityLevel.MODERATE: 1.55,
            ActivityLevel.ACTIVE: 1.725,
            ActivityLevel.VERY_ACTIVE: 1.9
        }

    def calculate_bmr(self, weight_kg: float, height_cm: float, age: int, gender: str, body_fat_pct: Optional[float] = None) -> float:
        if body_fat_pct is not None:
            lean_body_mass = weight_kg * (1 - (body_fat_pct / 100))
            return 370 + (21.6 * lean_body_mass)
        
        if gender.lower() == "male":
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    def calculate_tdee(self, weight_kg: float, height_cm: float, age: int, gender: str, activity_level: ActivityLevel, body_fat_pct: Optional[float] = None) -> float:
        bmr = self.calculate_bmr(weight_kg, height_cm, age, gender, body_fat_pct)
        multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        return round(bmr * multiplier, 2)

    def calculate_macros(self, tdee: float, weight_kg: float, goal: Goal, diet_preference: DietPreference = DietPreference.BALANCED, intensity: str = "moderate") -> Dict:
        """Calculates total calories and perfectly distributed macros based on RAG constants."""
        
        # Pull modifiers from science_constants.json
        caloric_modifiers = self.constants["caloric_modifiers"]
        protein_multipliers = self.constants["protein_multipliers"]
        
        if goal == Goal.BULK:
            surplus = caloric_modifiers["bulk_surplus"].get(intensity.lower(), 300)
            calories = tdee + surplus
            protein_mult = protein_multipliers["bulk"]
        elif goal == Goal.CUT:
            deficit = caloric_modifiers["cut_deficit"].get(intensity.lower(), 400)
            calories = tdee - deficit
            protein_mult = protein_multipliers["cut"]
        else:
            calories = tdee
            protein_mult = protein_multipliers["maintenance"]

        # Calculate Protein
        protein = round(weight_kg * protein_mult, 1)
        protein_cals = protein * 4

        # Calculate Fats based on Diet Preference
        if diet_preference == DietPreference.KETO:
            fat_pct = 0.70
        elif diet_preference == DietPreference.LOW_CARB:
            fat_pct = 0.40
        else: # BALANCED
            fat_pct = 0.25

        fat = round((calories * fat_pct) / 9, 1)
        fat_cals = fat * 9

        # Fill remaining calories with Carbs
        remaining_cals = calories - protein_cals - fat_cals
        carbs = round(max(0, remaining_cals / 4), 1)

        return {
            "goal": goal.value,
            "diet_preference": diet_preference.value,
            "intensity": intensity,
            "daily_calories": round(calories),
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "supplements": self.constants.get("supplements", {})
        }

    def calculate_training_volume(self, available_minutes: int, goal: Goal) -> Dict:
        """
        Combines RAG-derived optimal biological constants with hardcoded physical time constraints.
        Outputs min(optimal_from_rag, physical_max).
        """
        # 1. RAG Biological Constants
        vol_constants = self.constants["training_volume"]
        target = "strength" if goal == Goal.STRENGTH else "hypertrophy"
        
        optimal_exercises = vol_constants[target]["optimal_exercises"]
        optimal_sets = vol_constants[target]["optimal_sets_per_exercise"]
        rep_range = vol_constants[target]["rep_range"]
        rest_seconds = vol_constants[target]["rest_seconds"]

        # 2. Hardcoded Physical Clock Limits
        # Assume 1 set takes ~1 minute to perform, plus rest.
        minutes_per_set = 1 + (rest_seconds / 60)
        
        # Max exercises the user can physically fit into their time limit
        # (Assuming they do the optimal_sets for each exercise)
        max_physical_exercises = max(1, int(available_minutes / (minutes_per_set * optimal_sets)))
        
        # 3. The Merger
        actual_exercises = min(optimal_exercises, max_physical_exercises)

        return {
            "available_minutes": available_minutes,
            "goal": goal.value,
            "intensity": "high",
            "sets_per_exercise": optimal_sets,
            "exercises_per_session": actual_exercises,
            "rep_range": rep_range,
            "rest_between_sets_seconds": rest_seconds,
            "metadata": {
                "rag_optimal_exercises": optimal_exercises,
                "physical_ceiling": max_physical_exercises,
                "bottlenecked_by_time": max_physical_exercises < optimal_exercises
            }
        }
