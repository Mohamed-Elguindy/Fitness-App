def get_diet_system_prompt() -> str:
    return "You are a professional sports nutritionist."

def get_diet_prompt(meals_per_day: int, daily_targets: dict, meal_calorie_targets_text: str, sports_science_context: str, available_meals_json: str) -> str:
    return f"""
You are an elite, science-based sports nutritionist. 
Your task is to build a {meals_per_day}-meal diet plan that EXACTLY hits these daily targets:
- Calories: {daily_targets['daily_calories']} kcal
- Protein: {daily_targets['protein_g']}g
- Carbs: {daily_targets['carbs_g']}g
- Fat: {daily_targets['fat_g']}g

### EXACT CALORIE DISTRIBUTION (MANDATORY):
You MUST assign exactly these calories to the respective meals. Do not deviate.
{meal_calorie_targets_text}

### SPORTS SCIENCE CONTEXT (Follow this strictly):
{sports_science_context}

### AVAILABLE MEAL INVENTORY:
You MUST ONLY choose meals from this JSON inventory. Match light meals (like Greek Yogurt or Casein) to small calorie slots, and heavy meals (like Chicken Rice) to large calorie slots.
{available_meals_json}

Rules:
1. Choose exactly {meals_per_day} meals from the inventory. Use their EXACT names.
2. You MUST assign the `target_calories` to each meal EXACTLY as specified in the EXACT CALORIE DISTRIBUTION section above.
"""

def get_training_system_prompt() -> str:
    return "You are a professional strength and conditioning coach."

def get_training_program_prompt(days_per_week: int, goal: str, volume: dict, rag_context: str, available_exercises_json: str) -> str:
    return f"""
You are an elite, science-based strength and conditioning coach. 
Your task is to build a {days_per_week}-day training program for a {goal} goal.

### TARGET VOLUME SETTINGS (Hit these exactly):
- Sets per exercise: {volume['sets_per_exercise']}
- Exercises per session: {volume['exercises_per_session']}
- Rep range: {volume['rep_range']}
- Rest between sets: {volume['rest_between_sets_seconds']} seconds

### SPORTS SCIENCE CONTEXT (Follow this strictly):
{rag_context}

### AVAILABLE EXERCISE INVENTORY:
You MUST ONLY choose exercises from this JSON inventory. You cannot invent new exercises.
{available_exercises_json}

Rules:
1. Every single session MUST have exactly {volume['exercises_per_session']} exercises.
2. Every single exercise MUST have exactly {volume['sets_per_exercise']} sets.
3. Every single exercise MUST have the rep range '{volume['rep_range']}'.
4. Every single exercise MUST have a rest period of {volume['rest_between_sets_seconds']} seconds.
5. Provide a specific science-backed tip from the RAG context in the notes for each exercise.
6. MANDATORY MUSCLE COVERAGE: You have exactly {volume['exercises_per_session'] * days_per_week} total exercise slots for the entire week. You MUST assign at least 1 exercise to EVERY single major muscle group (Chest, Back, Quads, Hamstrings, Shoulders, Biceps, Triceps, Calves, Core) BEFORE you assign a second exercise to any muscle group. Do not ignore Hamstrings or Calves!
7. EXACT NAMES ONLY: You MUST use the exact `name` string from the JSON inventory provided. Do not shorten or modify names (e.g., use "Barbell Bench Press", NOT "Bench Press").
"""

def get_validation_retry_prompt(errors: list[str]) -> str:
    errors_str = "\n".join(errors)
    return f"Your generated program failed validation with the following errors:\n{errors_str}\nPlease correct your mistakes and regenerate the program."

def get_rag_diet_query(goal: str, dietary_restrictions: str) -> str:
    return f"What are the most important sports science rules for meal timing, protein distribution, and nutrient partitioning for a {goal} diet? Special considerations: {dietary_restrictions}."

def get_rag_training_query(goal: str, days_per_week: int, equipment: str, injuries: str) -> str:
    return f"What are the scientific rules for exercise selection, fatigue management, and volume for a {goal} program that trains {days_per_week} days a week using {equipment} equipment? Special injury considerations: {injuries}."

def get_rag_tool_descriptions() -> dict:
    return {
        "fitness": "Useful for answering physiological, nutritional, and workout programming questions about bulking, cutting, and gym exercises like bench press, deadlift, and lat pulldown.",
        "mentality": "Useful for addressing discipline, lack of motivation, fatigue, wanting to quit, or any psychological barriers using intense tough-love advice.",
        "general": "Useful for any question that is NOT related to fitness, gym training, nutrition, bulking, cutting, or workout mentality. Use this for all off-topic questions."
    }
