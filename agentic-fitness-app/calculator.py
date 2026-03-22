def calculate_tdee(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str) -> float:
    # Step 1: Calculate BMR using Mifflin-St Jeor formula
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Step 2: Multiply by activity multiplier
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    return round(bmr * multiplier, 2)

def calculate_macros(tdee: float, goal: str, weight_kg: float, intensity: str = "moderate") -> dict:
    bulk_surplus = {
        "lean": 200,
        "moderate": 300,
        "aggressive": 500
    }
    
    cut_deficit = {
        "lean": 200,
        "moderate": 400,
        "aggressive": 600
    }    
    if goal.lower() == "bulk":
        calories = tdee + bulk_surplus.get(intensity.lower(), 200)
        protein = round(weight_kg * 1.8, 1)
        fat = round((calories * 0.3) / 9, 1)
        carbs = round((calories - (protein * 4) - (fat * 9)) / 4, 1)
    elif goal.lower() == "cut":
        calories = tdee - cut_deficit.get(intensity.lower(), 400)
        protein = round(weight_kg * 2.2, 1)
        fat = round((calories * 0.20) / 9, 1)
        carbs = round((calories - (protein * 4) - (fat * 9)) / 4, 1)

    else:
        calories = tdee
        protein = round(weight_kg * 2.2, 1)
        fat = round((calories * 0.25) / 9, 1)
        carbs = round((calories - (protein * 4) - (fat * 9)) / 4, 1)



    return {
        "goal": goal,
        "intensity": intensity,
        "daily_calories": round(calories),
        "protein_g": protein,
        "carbs_g": carbs,
        "fat_g": fat
    }


def calculate_training_volume(available_minutes: int, goal: str) -> dict:
    
    if available_minutes <= 45:
        sets_per_exercise = 2
        exercises_per_session = 5
    elif available_minutes <= 75:
        sets_per_exercise = 3
        exercises_per_session = 6
    else:
        sets_per_exercise = 3
        exercises_per_session = 8

    if goal.lower() == "strength":
        rep_range = "3-6"
        rest_seconds = 180
    else:
        rep_range = "6-12"
        rest_seconds = 120

    return {
        "available_minutes": available_minutes,
        "goal": goal,
        "intensity":"high",
        "sets_per_exercise": sets_per_exercise,
        "exercises_per_session": exercises_per_session,
        "rep_range": rep_range,
        "rest_between_sets_seconds": rest_seconds
    }

