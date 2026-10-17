import json
from pathlib import Path
from typing import List, Dict, Optional

class MealService:
    def __init__(self):
        self.app_root = Path(__file__).resolve().parent.parent.parent
        self.data_path = self.app_root / "data" / "meals.json"
        self.meals = self._load_data()

    # --- Public API (The Headlines) ---

    def find(self, meal_type: str, budget: Optional[str] = None, cuisine: Optional[str] = None) -> List[Dict]:
        """Return meals of a specific type, optionally filtered by budget or cuisine with fallback."""
        base_meals = self.get_by_type(meal_type)
        results = base_meals

        if budget:
            results = self._filter_by_budget(results, budget)

        if cuisine:
            results = self._filter_by_cuisine(results, cuisine)

        return self._ensure_non_empty_fallback(results, fallback_meals=base_meals)

    def get_by_type(self, meal_type: str) -> List[Dict]:
        """Return all meals for a specific category (e.g., breakfasts, pre_workout)."""
        return self.meals.get(meal_type, [])

    # --- Filter & Fallback Helpers (Stepdown Order) ---

    def _filter_by_budget(self, meals: List[Dict], budget: str) -> List[Dict]:
        target_budget = budget.lower()
        return [meal for meal in meals if meal.get("budget_level", "").lower() == target_budget]

    def _filter_by_cuisine(self, meals: List[Dict], cuisine: str) -> List[Dict]:
        target_cuisine = cuisine.lower()
        return [meal for meal in meals if meal.get("cuisine", "").lower() == target_cuisine]

    def _ensure_non_empty_fallback(self, filtered_meals: List[Dict], fallback_meals: List[Dict]) -> List[Dict]:
        """Return fallback meals if filtering produced an empty list, ensuring the AI always has options."""
        return filtered_meals if filtered_meals else fallback_meals

    # --- Data Loading ---

    def _load_data(self) -> Dict[str, List[Dict]]:
        if not self.data_path.exists():
            return {}

        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)
