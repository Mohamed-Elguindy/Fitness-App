import json
from pathlib import Path
from typing import List, Dict, Optional

class MealService:
    def __init__(self):
        self.app_root = Path(__file__).resolve().parent.parent.parent
        self.data_path = self.app_root / "data" / "meals.json"
        self.meals = self._load_data()

    def _load_data(self) -> Dict[str, List[Dict]]:
        if not self.data_path.exists():
            return {}
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_meals_by_type(self, meal_type: str) -> List[Dict]:
        """Return all meals for a specific category (e.g., breakfasts, pre_workout)."""
        return self.meals.get(meal_type, [])

    def filter_meals(self, meal_type: str, budget: Optional[str] = None, cuisine: Optional[str] = None) -> List[Dict]:
        """Return meals of a specific type, optionally filtered by budget or cuisine."""
        meals_of_type = self.get_meals_by_type(meal_type)
        results = meals_of_type
        
        if budget:
            target_budget = budget.lower()
            results = [m for m in results if m.get("budget_level", "").lower() == target_budget]
            
        if cuisine:
            target_cuisine = cuisine.lower()
            results = [m for m in results if m.get("cuisine", "").lower() == target_cuisine]
            
        # Fallback: if filtering produces an empty list (e.g., they asked for high budget egyptian breakfast but we only have low budget), 
        # return the unfiltered list of that meal type so the AI always has options.
        if not results and meals_of_type:
            return meals_of_type
            
        return results
