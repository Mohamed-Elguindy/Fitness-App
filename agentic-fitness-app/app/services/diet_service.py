import json
import instructor
import google.generativeai as genai
from app.models.schemas import DietPlanRequest, DietPlan
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

    def _find_base_meal(self, meal_name: str, available_meals: dict) -> dict:
        normalized_meal_name = meal_name.lower()
        for _category, meals in available_meals.items():
            for meal in meals:
                if meal["name"].lower() == normalized_meal_name:
                    return meal
        return None

    def _scale_meal(self, base_meal: dict, target_calories: float) -> dict:
        scale_factor = target_calories / base_meal["base_calories"]
        
        scaled_ingredients = []
        for ingredient in base_meal["ingredients"]:
            scaled_ingredients.append({
                "food_name": ingredient["item"],
                "grams": round(ingredient["amount_g"] * scale_factor, 2)
            })
            
        return {
            "meal_name": base_meal["name"],
            "foods": scaled_ingredients,
            "total_calories": round(target_calories, 2),
            "total_protein": round(base_meal["macros"]["protein"] * scale_factor, 2),
            "total_carbs": round(base_meal["macros"]["carbs"] * scale_factor, 2),
            "total_fat": round(base_meal["macros"]["fat"] * scale_factor, 2)
        }

    def build_diet_plan(self, request: DietPlanRequest) -> dict:
        try:
            activity_level = ActivityLevel(request.activity_level.lower())
        except ValueError:
            activity_level = ActivityLevel.MODERATE
            
        try:
            goal = Goal(request.goal.lower())
        except ValueError:
            goal = Goal.MAINTENANCE

        tdee = self.calculator.calculate_tdee(request.weight_kg, request.height_cm, request.age, request.gender, activity_level)
        daily_targets = self.calculator.calculate_macros(tdee, request.weight_kg, goal, intensity=request.intensity)
        
        # Pull RAG Context
        sports_science_context = self.rag_service.get_diet_context(request.goal, dietary_restrictions="none")
        
        # Build Food Inventory
        available_meals = {
            "breakfasts": self.meal_service.find("breakfasts", request.budget),
            "lunches": self.meal_service.find("lunches", request.budget),
            "dinners": self.meal_service.find("dinners", request.budget),
            "pre_workout": self.meal_service.find("pre_workout", request.budget),
            "post_workout": self.meal_service.find("post_workout", request.budget),
            "before_bed": self.meal_service.find("before_bed", request.budget)
        }
        
        available_meals_json = json.dumps(available_meals, indent=2)
        
        meal_calorie_targets = self.calculator.calculate_meal_distribution(daily_targets['daily_calories'], request.meals_per_day)
        meal_calorie_targets_text = "\n".join([f"- {target['meal_time']}: {target['target_calories']} kcal" for target in meal_calorie_targets])

        diet_plan_prompt = get_diet_prompt(
            request.meals_per_day,
            daily_targets,
            meal_calorie_targets_text,
            sports_science_context,
            available_meals_json
        )

        llm_plan: DietPlan = self.structured_client.chat.completions.create(
            response_model=DietPlan,
            messages=[
                {"role": "system", "content": get_diet_system_prompt()},
                {"role": "user", "content": diet_plan_prompt}
            ]
        )

        # Scale the meals perfectly using Python
        scaled_meals = []
        for selection in llm_plan.meals:
            base_meal = self._find_base_meal(selection.meal_name, available_meals)
            if base_meal:
                scaled_meal = self._scale_meal(base_meal, selection.target_calories)
                scaled_meal["meal_time"] = selection.meal_time
                scaled_meals.append(scaled_meal)
            else:
                print(f"WARNING: LLM Hallucinated meal '{selection.meal_name}'.")

        # Recalculate top-level macros based on actual scaled meals to ensure math is perfectly accurate
        actual_calories = sum(meal["total_calories"] for meal in scaled_meals)
        actual_protein = sum(meal["total_protein"] for meal in scaled_meals)
        actual_carbs = sum(meal["total_carbs"] for meal in scaled_meals)
        actual_fat = sum(meal["total_fat"] for meal in scaled_meals)

        return {
            "tdee": tdee,
            "macros": daily_targets,
            "meal_plan": {
                "meals": scaled_meals,
                "daily_calories": round(actual_calories, 2),
                "daily_protein": round(actual_protein, 2),
                "daily_carbs": round(actual_carbs, 2),
                "daily_fat": round(actual_fat, 2)
            }
        }

    def stream_diet_plan(self, request: DietPlanRequest):
        yield {"status": "initializing nutrition core..."}

        try:
            activity_level = ActivityLevel(request.activity_level.lower())
        except ValueError:
            activity_level = ActivityLevel.MODERATE
            
        try:
            goal = Goal(request.goal.lower())
        except ValueError:
            goal = Goal.MAINTENANCE

        yield {"status": "calculating metabolic rate (TDEE)..."}
        tdee = self.calculator.calculate_tdee(request.weight_kg, request.height_cm, request.age, request.gender, activity_level)
        
        yield {"status": "calculating optimal macronutrient split..."}
        daily_targets = self.calculator.calculate_macros(tdee, request.weight_kg, goal, intensity=request.intensity)
        
        yield {"status": "querying sports science literature..."}
        sports_science_context = self.rag_service.get_diet_context(request.goal, dietary_restrictions="none")
        
        yield {"status": "building food inventory..."}
        available_meals = {
            "breakfasts": self.meal_service.find("breakfasts", request.budget),
            "lunches": self.meal_service.find("lunches", request.budget),
            "dinners": self.meal_service.find("dinners", request.budget),
            "pre_workout": self.meal_service.find("pre_workout", request.budget),
            "post_workout": self.meal_service.find("post_workout", request.budget),
            "before_bed": self.meal_service.find("before_bed", request.budget)
        }
        
        available_meals_json = json.dumps(available_meals, indent=2)
        
        meal_calorie_targets = self.calculator.calculate_meal_distribution(daily_targets['daily_calories'], request.meals_per_day)
        meal_calorie_targets_text = "\n".join([f"- {target['meal_time']}: {target['target_calories']} kcal" for target in meal_calorie_targets])

        diet_plan_prompt = get_diet_prompt(
            request.meals_per_day,
            daily_targets,
            meal_calorie_targets_text,
            sports_science_context,
            available_meals_json
        )

        yield {"status": "generating meal plan..."}
        llm_plan: DietPlan = self.structured_client.chat.completions.create(
            response_model=DietPlan,
            messages=[
                {"role": "system", "content": get_diet_system_prompt()},
                {"role": "user", "content": diet_plan_prompt}
            ]
        )

        yield {"status": "scaling ingredients perfectly..."}
        scaled_meals = []
        for selection in llm_plan.meals:
            base_meal = self._find_base_meal(selection.meal_name, available_meals)
            if base_meal:
                scaled_meal = self._scale_meal(base_meal, selection.target_calories)
                scaled_meal["meal_time"] = selection.meal_time
                scaled_meals.append(scaled_meal)

        # Recalculate top-level macros based on actual scaled meals to ensure math is perfectly accurate
        actual_calories = sum(meal["total_calories"] for meal in scaled_meals)
        actual_protein = sum(meal["total_protein"] for meal in scaled_meals)
        actual_carbs = sum(meal["total_carbs"] for meal in scaled_meals)
        actual_fat = sum(meal["total_fat"] for meal in scaled_meals)

        yield {
            "result": {
                "tdee": tdee,
                "macros": daily_targets,
                "meal_plan": {
                    "meals": scaled_meals,
                    "daily_calories": round(actual_calories, 2),
                    "daily_protein": round(actual_protein, 2),
                    "daily_carbs": round(actual_carbs, 2),
                    "daily_fat": round(actual_fat, 2)
                }
            }
        }
