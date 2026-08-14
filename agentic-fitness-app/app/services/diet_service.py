import json
import instructor
import google.generativeai as genai
from app.models.schemas import DietPlanRequest, DietPlan
from app.services.meal_service import MealService
from app.services.rag_service import RAGService
from app.utils.calculator import CalculatorService, ActivityLevel, Goal

class DietService:
    def __init__(self, llm_client: genai.GenerativeModel):
        self.client = instructor.from_gemini(client=llm_client, mode=instructor.Mode.GEMINI_JSON)
        self.meal_service = MealService()
        self.rag_service = RAGService()
        self.calc = CalculatorService()

    def _get_base_meal(self, meal_name: str, inventory: dict) -> dict:
        target_name = meal_name.lower()
        for category, meals in inventory.items():
            for meal in meals:
                if meal["name"].lower() == target_name:
                    return meal
        return None

    def _scale_meal(self, base_meal: dict, target_calories: float) -> dict:
        ratio = target_calories / base_meal["base_calories"]
        
        scaled_ingredients = []
        for ing in base_meal["ingredients"]:
            scaled_ingredients.append({
                "food_name": ing["item"],
                "grams": round(ing["amount_g"] * ratio, 2)
            })
            
        return {
            "meal_name": base_meal["name"],
            "foods": scaled_ingredients,
            "total_calories": round(target_calories, 2),
            "total_protein": round(base_meal["macros"]["protein"] * ratio, 2),
            "total_carbs": round(base_meal["macros"]["carbs"] * ratio, 2),
            "total_fat": round(base_meal["macros"]["fat"] * ratio, 2)
        }

    def build_diet_plan(self, request: DietPlanRequest) -> dict:
        try:
            activity = ActivityLevel(request.activity_level.lower())
        except ValueError:
            activity = ActivityLevel.MODERATE
            
        try:
            goal_enum = Goal(request.goal.lower())
        except ValueError:
            goal_enum = Goal.MAINTENANCE

        tdee = self.calc.calculate_tdee(request.weight_kg, request.height_cm, request.age, request.gender, activity)
        macros = self.calc.calculate_macros(tdee, request.weight_kg, goal_enum, intensity=request.intensity)
        
        # Pull RAG Context
        rag_context = self.rag_service.get_diet_context(request.goal, dietary_restrictions="none")
        
        # Build Food Inventory
        inventory = {
            "breakfasts": self.meal_service.filter_meals("breakfasts", request.budget),
            "lunches": self.meal_service.filter_meals("lunches", request.budget),
            "dinners": self.meal_service.filter_meals("dinners", request.budget),
            "pre_workout": self.meal_service.filter_meals("pre_workout", request.budget),
            "post_workout": self.meal_service.filter_meals("post_workout", request.budget),
            "before_bed": self.meal_service.filter_meals("before_bed", request.budget)
        }
        
        inventory_str = json.dumps(inventory, indent=2)
        
        meal_targets = self.calc.calculate_meal_distribution(macros['daily_calories'], request.meals_per_day)
        targets_str = "\n".join([f"- {t['meal_time']}: {t['target_calories']} kcal" for t in meal_targets])

        prompt = f"""
You are an elite, science-based sports nutritionist. 
Your task is to build a {request.meals_per_day}-meal diet plan that EXACTLY hits these daily targets:
- Calories: {macros['daily_calories']} kcal
- Protein: {macros['protein_g']}g
- Carbs: {macros['carbs_g']}g
- Fat: {macros['fat_g']}g

### EXACT CALORIE DISTRIBUTION (MANDATORY):
You MUST assign exactly these calories to the respective meals. Do not deviate.
{targets_str}

### SPORTS SCIENCE CONTEXT (Follow this strictly):
{rag_context}

### AVAILABLE MEAL INVENTORY:
You MUST ONLY choose meals from this JSON inventory. Match light meals (like Greek Yogurt or Casein) to small calorie slots, and heavy meals (like Chicken Rice) to large calorie slots.
{inventory_str}

Rules:
1. Choose exactly {request.meals_per_day} meals from the inventory. Use their EXACT names.
2. You MUST assign the `target_calories` to each meal EXACTLY as specified in the EXACT CALORIE DISTRIBUTION section above.
"""

        plan: DietPlan = self.client.chat.completions.create(
            response_model=DietPlan,
            messages=[
                {"role": "system", "content": "You are a professional sports nutritionist."},
                {"role": "user", "content": prompt}
            ]
        )

        # Scale the meals perfectly using Python
        final_meals = []
        for selection in plan.meals:
            base_meal = self._get_base_meal(selection.meal_name, inventory)
            if base_meal:
                scaled = self._scale_meal(base_meal, selection.target_calories)
                scaled["meal_time"] = selection.meal_time
                final_meals.append(scaled)
            else:
                print(f"WARNING: LLM Hallucinated meal '{selection.meal_name}'.")

        # Recalculate top-level macros based on actual scaled meals to ensure math is perfectly accurate
        actual_calories = sum(m["total_calories"] for m in final_meals)
        actual_protein = sum(m["total_protein"] for m in final_meals)
        actual_carbs = sum(m["total_carbs"] for m in final_meals)
        actual_fat = sum(m["total_fat"] for m in final_meals)

        return {
            "tdee": tdee,
            "macros": macros,
            "meal_plan": {
                "meals": final_meals,
                "daily_calories": round(actual_calories, 2),
                "daily_protein": round(actual_protein, 2),
                "daily_carbs": round(actual_carbs, 2),
                "daily_fat": round(actual_fat, 2)
            }
        }

    def stream_diet_plan(self, request: DietPlanRequest):
        yield {"status": "initializing nutrition core..."}

        try:
            activity = ActivityLevel(request.activity_level.lower())
        except ValueError:
            activity = ActivityLevel.MODERATE
            
        try:
            goal_enum = Goal(request.goal.lower())
        except ValueError:
            goal_enum = Goal.MAINTENANCE

        yield {"status": "calculating metabolic rate (TDEE)..."}
        tdee = self.calc.calculate_tdee(request.weight_kg, request.height_cm, request.age, request.gender, activity)
        
        yield {"status": "calculating optimal macronutrient split..."}
        macros = self.calc.calculate_macros(tdee, request.weight_kg, goal_enum, intensity=request.intensity)
        
        yield {"status": "querying sports science literature..."}
        rag_context = self.rag_service.get_diet_context(request.goal, dietary_restrictions="none")
        
        yield {"status": "building food inventory..."}
        inventory = {
            "breakfasts": self.meal_service.filter_meals("breakfasts", request.budget),
            "lunches": self.meal_service.filter_meals("lunches", request.budget),
            "dinners": self.meal_service.filter_meals("dinners", request.budget),
            "pre_workout": self.meal_service.filter_meals("pre_workout", request.budget),
            "post_workout": self.meal_service.filter_meals("post_workout", request.budget),
            "before_bed": self.meal_service.filter_meals("before_bed", request.budget)
        }
        
        inventory_str = json.dumps(inventory, indent=2)
        
        meal_targets = self.calc.calculate_meal_distribution(macros['daily_calories'], request.meals_per_day)
        targets_str = "\n".join([f"- {t['meal_time']}: {t['target_calories']} kcal" for t in meal_targets])

        prompt = f"""
You are an elite, science-based sports nutritionist. 
Your task is to build a {request.meals_per_day}-meal diet plan that EXACTLY hits these daily targets:
- Calories: {macros['daily_calories']} kcal
- Protein: {macros['protein_g']}g
- Carbs: {macros['carbs_g']}g
- Fat: {macros['fat_g']}g

### EXACT CALORIE DISTRIBUTION (MANDATORY):
You MUST assign exactly these calories to the respective meals. Do not deviate.
{targets_str}

### SPORTS SCIENCE CONTEXT (Follow this strictly):
{rag_context}

### AVAILABLE MEAL INVENTORY:
You MUST ONLY choose meals from this JSON inventory. Match light meals (like Greek Yogurt or Casein) to small calorie slots, and heavy meals (like Chicken Rice) to large calorie slots.
{inventory_str}

Rules:
1. Choose exactly {request.meals_per_day} meals from the inventory. Use their EXACT names.
2. You MUST assign the `target_calories` to each meal EXACTLY as specified in the EXACT CALORIE DISTRIBUTION section above.
"""

        yield {"status": "generating meal plan..."}
        plan: DietPlan = self.client.chat.completions.create(
            response_model=DietPlan,
            messages=[
                {"role": "system", "content": "You are a professional sports nutritionist."},
                {"role": "user", "content": prompt}
            ]
        )

        yield {"status": "scaling ingredients perfectly..."}
        final_meals = []
        for selection in plan.meals:
            base_meal = self._get_base_meal(selection.meal_name, inventory)
            if base_meal:
                scaled = self._scale_meal(base_meal, selection.target_calories)
                scaled["meal_time"] = selection.meal_time
                final_meals.append(scaled)

        # Recalculate top-level macros based on actual scaled meals to ensure math is perfectly accurate
        actual_calories = sum(m["total_calories"] for m in final_meals)
        actual_protein = sum(m["total_protein"] for m in final_meals)
        actual_carbs = sum(m["total_carbs"] for m in final_meals)
        actual_fat = sum(m["total_fat"] for m in final_meals)

        yield {
            "result": {
                "tdee": tdee,
                "macros": macros,
                "meal_plan": {
                    "meals": final_meals,
                    "daily_calories": round(actual_calories, 2),
                    "daily_protein": round(actual_protein, 2),
                    "daily_carbs": round(actual_carbs, 2),
                    "daily_fat": round(actual_fat, 2)
                }
            }
        }
