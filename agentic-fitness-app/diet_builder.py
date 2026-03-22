import os
from groq import Groq
from dotenv import load_dotenv
from calculator import calculate_tdee, calculate_macros
from schemas import DietPlanRequest

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def calculate_meal_distribution(daily_calories: float, meals_per_day: int) -> list:
    
    distributions = {
        1: [1.0],
        2: [0.4, 0.6],
        3: [0.3, 0.4, 0.3],
        4: [0.25, 0.30, 0.25, 0.20],
        5: [0.20, 0.25, 0.20, 0.20, 0.15],
        6: [0.20, 0.25, 0.15, 0.15, 0.15, 0.10]
    }

    percentages = distributions.get(meals_per_day, distributions[3])
    
    return [round(daily_calories * pct) for pct in percentages]

def build_prompt(macros: dict, request: DietPlanRequest) -> str:
    
    budget_foods = {
        "low": {
            "proteins": "eggs, tuna, cottage cheese",
            "carbs": "oats, white rice, banana, whole wheat bread",
            "fats": "peanut butter, olive oil"
        },
        "moderate": {
            "proteins": "eggs, tuna, chicken breast, greek yogurt, cottage cheese, whey protein",
            "carbs": "oats, white rice, sweet potato, banana, whole wheat bread, pasta",
            "fats": "peanut butter, olive oil, almonds"
        },
        "high": {
            "proteins": "eggs, tuna, chicken breast, ground beef 90% lean, greek yogurt, cottage cheese, whey protein",
            "carbs": "oats, white rice, sweet potato, banana, whole wheat bread, pasta, white bread",
            "fats": "peanut butter, olive oil, almonds, avocado, dark chocolate 70%"
        }
    }

    selected_foods = budget_foods.get(request.budget.lower(), budget_foods["moderate"])
    meal_calories = calculate_meal_distribution(macros["daily_calories"], request.meals_per_day)
    meal_targets = "\n".join([f"- Meal {i+1}: exactly {cal} calories" for i, cal in enumerate(meal_calories)])

    return f"""
You are a professional sports nutritionist. Build a detailed meal plan for this person:

Goal: {request.goal}
Intensity: {request.intensity}
Number of meals: {request.meals_per_day}
Budget level: {request.budget}

Daily targets to hit exactly:
- Calories: {macros['daily_calories']} kcal
- Protein: {macros['protein_g']}g
- Carbs: {macros['carbs_g']}g
- Fat: {macros['fat_g']}g

Each meal MUST hit these exact calorie targets:
{meal_targets}

Only use these foods based on the budget level:
Proteins: {selected_foods['proteins']}
Carbs: {selected_foods['carbs']}
Fats: {selected_foods['fats']}

Food combination rules — this is MANDATORY, never break these rules:
- NEVER mix fish (tuna) with any dairy (greek yogurt, cottage cheese, whey protein) in the same meal
- NEVER put whey protein shake in the same meal as eggs
- NEVER put whey protein shake in the same meal as bread
- whey protein shake ONLY pairs with banana alone or oats alone, nothing else
- Greek yogurt ONLY appears in breakfast, never in any other meal
- Cottage cheese ONLY appears in the before bed meal, never anywhere else
- Dark chocolate ONLY appears as the before bed snack, never in any other meal
- Pasta and rice NEVER appear in the same meal
- Olive oil ONLY pairs with chicken, beef, or fish, never with oats or whey
- Tuna ONLY pairs with rice or sweet potato, nothing else
- Eggs ONLY pair with oats, never with bread or whey
- Peanut butter ONLY pairs with oats or cottage cheese, never with bread
- Before bed meal MUST be moderate carbs — cottage cheese with bread or greek yogurt with oats or banana.

Meal timing rules:
- Pre workout meal must be high carb — use rice, pasta, or oats
- Post workout meal must be high protein and moderate carb — use whey protein, banana, bread
- Before bed meal must be high protein zero carb — cottage cheese and peanut butter only
- Breakfast must be balanced — use eggs or oats as base

Rules:
- Each meal must show exact grams of each food
- Each meal must show its calories, protein, carbs, fat
- All meals combined must add up exactly to the daily targets
- Respond in JSON format only, no extra text

JSON format:
{{
    "meals": [
        {{
            "meal_name": "Breakfast",
            "timing": "8:00 AM",
            "foods": [
                {{"food": "oats", "grams": 100, "calories": 380, "protein": 13, "carbs": 66, "fat": 7}}
            ],
            "meal_totals": {{"calories": 380, "protein": 13, "carbs": 66, "fat": 7}}
        }}
    ],
    "daily_totals": {{"calories": 0, "protein": 0, "carbs": 0, "fat": 0}}
}}
"""

def call_llm(prompt: str) -> dict:
    import json
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional sports nutritionist. Always respond in valid JSON only. No extra text, no markdown, no backticks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    raw = response.choices[0].message.content
    cleaned = raw.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned)

def build_diet_plan(request: DietPlanRequest) -> dict:
    
    tdee = calculate_tdee(request.weight_kg, request.height_cm, request.age, request.gender, request.activity_level)
    macros = calculate_macros(tdee, request.goal, request.weight_kg, request.intensity)
    prompt = build_prompt(macros, request)
    
    meal_plan = None
    attempts = 0
    
    while meal_plan is None and attempts < 3:
        raw_plan = call_llm(prompt)
        meal_plan = validate_meal_plan(raw_plan, macros["daily_calories"])
        attempts += 1

    return {
        "tdee": tdee,
        "macros": macros,
        "meal_plan": meal_plan
    }

def check_rules(meal_plan: dict) -> bool:
    
    for meal in meal_plan["meals"]:
        foods = [f["food"].lower() for f in meal["foods"]]
        meal_name = meal["meal_name"].lower()

        # Never mix tuna with dairy
        if "tuna" in foods and any(f in foods for f in ["greek yogurt", "cottage cheese", "whey protein"]):
            print(f"Rule broken: tuna mixed with dairy in {meal_name}")
            return False

        # Never mix two main proteins
        if "chicken breast" in foods and "tuna" in foods:
            print(f"Rule broken: two proteins in same meal in {meal_name}")
            return False

        # Whey never with eggs
        if "whey protein" in foods and "eggs" in foods:
            print(f"Rule broken: whey with eggs in {meal_name}")
            return False

    return True

def validate_meal_plan(meal_plan: dict, target_calories: float) -> dict:
    
    total_calories = meal_plan["daily_totals"]["calories"]
    difference = abs(total_calories - target_calories)
    
    if difference > 100:
        print(f"Calories off by {difference} — retrying...")
        return None
    
    if not check_rules(meal_plan):
        print("Rules broken — retrying...")
        return None
    
    return meal_plan