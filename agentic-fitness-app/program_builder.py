import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
from calculator import calculate_training_volume
from schemas import TrainingProgramRequest

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_program_prompt(volume: dict, request: TrainingProgramRequest) -> str:

    gym_exercises = """
    CHEST: bench press, incline bench press, machine pec deck, weighted dips
    BACK: lat pulldown, cable rows, chest supported t-bar row, pull up, deadlift
    SHOULDERS: overhead press, lateral raise, reverse pec deck, dumbbell shrugs
    BICEPS: barbell curl, dumbbell curl, bayesian cable curl, preacher curl
    TRICEPS: tricep pushdown, overhead cable tricep extension, skull crushers
    LEGS: squat, romanian deadlift, leg extension, seated leg curl, walking lunge, nautilus glute drive, standing calf raise
    CORE: cable crunch
    """

    home_exercises = """
    CHEST: push ups, wide push ups, weighted dips
    BACK: pull up, bodyweight rows
    SHOULDERS: pike push ups, lateral raise with water bottles
    BICEPS: bodyweight curl, hammer curl with water bottles
    TRICEPS: diamond push ups, bench dips
    LEGS: squat, walking lunge, romanian deadlift, calf raise
    CORE: plank, crunches
    """

    exercises = gym_exercises if request.equipment == "gym" else home_exercises
    split_structure = {
        1: ["Full Body"],
        2: ["Full Body", "Full Body"],
        3: ["Full Body", "Full Body", "Full Body"],
        4: ["Upper Body", "Lower Body", "Upper Body", "Lower Body"],
        5: ["Push", "Pull", "Legs", "Upper Body", "Lower Body"],
        6: ["Push", "Pull", "Legs", "Push", "Pull", "Legs"],
        7: ["Push", "Pull", "Legs", "Push", "Pull", "Legs", "Rest"]
    }

    selected_split = split_structure.get(request.days_per_week, split_structure[3])
    split_info = "\n".join([f"- Day {i+1}: {day}" for i, day in enumerate(selected_split)])

    return f"""
You are a professional strength and conditioning coach. Build a detailed weekly training program for this person:

Goal: {request.goal}
Days per week: {request.days_per_week}
Available time per session: {request.available_minutes} minutes
Equipment: {request.equipment}
Intensity: {volume['intensity']}
Sets per exercise: {volume['sets_per_exercise']}
Exercises per session: {volume['exercises_per_session']}
Rep range: {volume['rep_range']}
Rest between sets: {volume['rest_between_sets_seconds']} seconds

Available exercises:
{exercises}

Training split structure — follow this EXACTLY:
{split_info}

Rules for each split:
- Full Body: include at least one exercise for chest, back, shoulders, biceps, triceps, legs
- Upper Body: include chest, back, shoulders, biceps, triceps only
- Lower Body: include quads, hamstrings, glutes, calves only
- Push: include chest, shoulders, triceps only
- Pull: include back, biceps only
- Legs: include quads, hamstrings, glutes, calves only
- Rest day: no exercises, just recovery

Rules:
- Never train the same muscle group on consecutive days
- Each session must have exactly {volume['exercises_per_session']} exercises
- Each exercise must have exactly {volume['sets_per_exercise']} sets
- Rep range for every exercise is {volume['rep_range']}
- Rest between sets is {volume['rest_between_sets_seconds']} seconds
- Distribute muscle groups intelligently across {request.days_per_week} days
- If goal is strength focus on compound movements first
- If goal is hypertrophy include both compound and isolation movements
- Respond in JSON format only, no extra text

JSON format:
{{
    "program_name": "name of the program",
    "days_per_week": {request.days_per_week},
    "goal": "{request.goal}",
    "sessions": [
        {{
            "day": "Day 1",
            "focus": "muscle groups trained",
            "exercises": [
                {{
                    "exercise": "bench press",
                    "sets": {volume['sets_per_exercise']},
                    "reps": "{volume['rep_range']}",
                    "rest_seconds": {volume['rest_between_sets_seconds']},
                    "notes": "progression tip"
                }}
            ]
        }}
    ]
}}
"""
def call_llm(prompt: str) -> dict:
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional strength and conditioning coach. Always respond in valid JSON only. No extra text, no markdown, no backticks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    raw = response.choices[0].message.content
    cleaned = raw.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned)

def build_training_program(request: TrainingProgramRequest) -> dict:
    
    volume = calculate_training_volume(request.available_minutes, request.goal)
    prompt = build_program_prompt(volume, request)
    program = call_llm(prompt)

    return {
        "volume_settings": volume,
        "program": program
    }