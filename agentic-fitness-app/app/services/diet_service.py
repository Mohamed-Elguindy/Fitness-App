import json
import instructor
import google.generativeai as genai
from app.models.schemas import DietPlanRequest, DietPlan, MealSelection
from app.services.meal_service import MealService
from app.services.rag_service import RAGService
from app.utils.calculator import CalculatorService, ActivityLevel, Goal
from app.utils.prompts import get_diet_prompt, get_diet_system_prompt

class DietService:
    def __init__(self, llm_client: genai.GenerativeModel):
        self.structured_client = instructor.from_gemini(client=llm_client, mode=instructor.Mode.GEMINI_JSON)
        self.meal_service = MealService()
        self.rag_service = RAGService()
        self.calculator = CalculatorService()

    # --- Public API Endpoints ---

    def build_diet_plan(self, request: DietPlanRequest) -> dict:
        tdee, daily_targets = self._calculate_nutrition_targets(request)
        available_meals = self._get_available_meals(request.budget)
        
        meal_selections = self._select_meals(request, daily_targets, available_meals)
        scaled_meals = self._scale_selected_meals(meal_selections, available_meals)
        daily_nutrition = self._calculate_total_nutrition(scaled_meals)

        return {
            "tdee": tdee,
            "macros": daily_targets,
            "meal_plan": {
                "meals": scaled_meals,
                **daily_nutrition
            }
        }

    def stream_diet_plan(self, request: DietPlanRequest):
        yield {"status": "initializing nutrition core..."}

        yield {"status": "calculating metabolic rate & optimal macros..."}
        tdee, daily_targets = self._calculate_nutrition_targets(request)

        yield {"status": "building food inventory..."}
        available_meals = self._get_available_meals(request.budget)

        yield {"status": "generating meal plan..."}
        meal_selections = self._select_meals(request, daily_targets, available_meals)

        yield {"status": "scaling ingredients perfectly..."}
        scaled_meals = self._scale_selected_meals(meal_selections, available_meals)
        daily_nutrition = self._calculate_total_nutrition(scaled_meals)

        yield {
            "result": {
                "tdee": tdee,
                "macros": daily_targets,
                "meal_plan": {
                    "meals": scaled_meals,
                    **daily_nutrition
                }
            }
        }

    # --- Pipeline Helpers (Stepdown Order) ---

    def _calculate_nutrition_targets(self, request: DietPlanRequest) -> tuple[float, dict]:
        try:
            activity_level = ActivityLevel(request.activity_level.lower())
        except ValueError:
            activity_level = ActivityLevel.MODERATE
            
        try:
            goal = Goal(request.goal.lower())
        except ValueError:
            goal = Goal.MAINTENANCE

        tdee = self.calculator.calculate_tdee(
            request.weight_kg, 
            request.height_cm, 
            request.age, 
            request.gender, 
            activity_level
        )
        daily_targets = self.calculator.calculate_macros(
            tdee, 
            request.weight_kg, 
            goal, 
            intensity=request.intensity
        )
        return tdee, daily_targets

    def _get_available_meals(self, budget: str) -> dict:
        categories = ["breakfasts", "lunches", "dinners", "pre_workout", "post_workout", "before_bed"]
        return {category: self.meal_service.find(category, budget) for category in categories}

    def _select_meals(self, request: DietPlanRequest, daily_targets: dict, available_meals: dict) -> DietPlan:
        sports_science_context = self.rag_service.get_diet_context(request.goal, dietary_restrictions="none")
        available_meals_json = json.dumps(available_meals, indent=2)
        meal_calorie_targets_text = self._format_meal_calorie_targets(daily_targets["daily_calories"], request.meals_per_day)

        diet_plan_prompt = get_diet_prompt(
            request.meals_per_day,
            daily_targets,
            meal_calorie_targets_text,
            sports_science_context,
            available_meals_json
        )

        return self.structured_client.chat.completions.create(
            response_model=DietPlan,
            messages=[
                {"role": "system", "content": get_diet_system_prompt()},
                {"role": "user", "content": diet_plan_prompt}
            ]
        )

    def _format_meal_calorie_targets(self, daily_calories: float, meals_per_day: int) -> str:
        meal_calorie_targets = self.calculator.calculate_meal_distribution(daily_calories, meals_per_day)
        return "\n".join([f"- {target['meal_time']}: {target['target_calories']} kcal" for target in meal_calorie_targets])

    def _scale_selected_meals(self, meal_selections: DietPlan, available_meals: dict) -> list[dict]:
        scaled_meals = []
        for selection in meal_selections.meals:
            base_meal = self._find_base_meal(selection.meal_name, available_meals)
            if base_meal:
                scaled_meals.append(self._scale_meal(base_meal, selection))
            else:
                print(f"WARNING: LLM Hallucinated meal '{selection.meal_name}'.")
        return scaled_meals

    def _find_base_meal(self, meal_name: str, available_meals: dict) -> dict | None:
        normalized_meal_name = meal_name.lower()
        for meals in available_meals.values():
            for meal in meals:
                if meal["name"].lower() == normalized_meal_name:
                    return meal
        return None

    def _scale_meal(self, base_meal: dict, selection: MealSelection) -> dict:
        scale_factor = selection.target_calories / base_meal["base_calories"]
        
        return {
            "meal_name": base_meal["name"],
            "meal_time": selection.meal_time,
            "foods": self._scale_ingredients(base_meal["ingredients"], scale_factor),
            "total_calories": round(selection.target_calories, 2),
            "total_protein": round(base_meal["macros"]["protein"] * scale_factor, 2),
            "total_carbs": round(base_meal["macros"]["carbs"] * scale_factor, 2),
            "total_fat": round(base_meal["macros"]["fat"] * scale_factor, 2)
        }

    def _scale_ingredients(self, ingredients: list[dict], scale_factor: float) -> list[dict]:
        return [
            {
                "food_name": ingredient["item"],
                "grams": round(ingredient["amount_g"] * scale_factor, 2)
            }
            for ingredient in ingredients
        ]

    def _calculate_total_nutrition(self, scaled_meals: list[dict]) -> dict:
        actual_calories = sum(meal["total_calories"] for meal in scaled_meals)
        actual_protein = sum(meal["total_protein"] for meal in scaled_meals)
        actual_carbs = sum(meal["total_carbs"] for meal in scaled_meals)
        actual_fat = sum(meal["total_fat"] for meal in scaled_meals)

        return {
            "daily_calories": round(actual_calories, 2),
            "daily_protein": round(actual_protein, 2),
            "daily_carbs": round(actual_carbs, 2),
            "daily_fat": round(actual_fat, 2)
        }
