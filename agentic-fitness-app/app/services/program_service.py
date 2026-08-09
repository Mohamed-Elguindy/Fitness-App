import json
import instructor
import google.generativeai as genai
from app.models.schemas import TrainingProgramRequest, TrainingProgram
from app.services.exercise_service import ExerciseService
from app.services.rag_service import RAGService
from app.utils.calculator import CalculatorService, Goal

class ProgramService:
    def __init__(self, llm_client: genai.GenerativeModel):
        self.client = instructor.from_gemini(client=llm_client, mode=instructor.Mode.GEMINI_JSON)
        self.exercise_service = ExerciseService()
        self.rag_service = RAGService()
        self.calc = CalculatorService()

    def _validate_program(self, program: TrainingProgram, inventory: list, days_per_week: int) -> list[str]:
        errors = []
        allowed_exercises = {ex["name"].lower(): ex for ex in inventory}
        
        # 1. Check for exact names and duplicates
        used_exercises = set()
        for session in program.sessions:
            for exercise in session.exercises:
                ex_name = exercise.exercise_name.lower()
                if ex_name not in allowed_exercises:
                    errors.append(f"Exercise '{exercise.exercise_name}' is not in the inventory. You MUST pick EXACT names from the inventory provided.")
                else:
                    if ex_name in used_exercises:
                        errors.append(f"You used '{exercise.exercise_name}' more than once in the program. You must select a unique exercise for every single slot.")
                    used_exercises.add(ex_name)
                    
        # 2. Check Primary Muscle Coverage
        hit_primary_muscles = set()
        for session in program.sessions:
            for exercise in session.exercises:
                ex_name = exercise.exercise_name.lower()
                if ex_name in allowed_exercises:
                    ex_data = allowed_exercises[ex_name]
                    if "primary_muscle" in ex_data:
                        hit_primary_muscles.add(ex_data["primary_muscle"].lower())
                        
        # Required macro groups must be hit as PRIMARY muscles
        hit_str = " ".join(hit_primary_muscles)
        required = ["chest", "back", "quadriceps", "hamstrings", "shoulder", "bicep", "tricep", "calves"]
        missing = [req for req in required if req not in hit_str and req + "s" not in hit_str]
        
        if missing:
            errors.append(f"Your program forgot to include exercises that target: {', '.join(missing)} AS A PRIMARY MUSCLE. You must include at least one isolation or compound exercise where these are the PRIMARY focus.")

        # 3. Check that the primary muscles targeted align with the session's focus_muscles
        for session in program.sessions:
            focus_str = " ".join(session.focus_muscles).lower()
            for exercise in session.exercises:
                ex_name = exercise.exercise_name.lower()
                if ex_name in allowed_exercises:
                    primary = allowed_exercises[ex_name].get("primary_muscle", "").lower()
                    if primary and primary not in focus_str and primary[:-1] not in focus_str:
                         errors.append(f"In session '{session.day_name}', you included '{exercise.exercise_name}' (targets {primary}), but the focus muscles for this day are: {', '.join(session.focus_muscles)}. Please replace it with an exercise that matches the day's focus.")

        return errors

    def build_training_program(self, request: TrainingProgramRequest) -> dict:
        try:
            goal_enum = Goal(request.goal.lower())
        except ValueError:
            goal_enum = Goal.HYPERTROPHY

        volume = self.calc.calculate_training_volume(request.available_minutes, goal_enum)
        
        # Pull RAG Context
        injuries = request.injuries if request.injuries else "none"
        rag_context = self.rag_service.get_training_context(
            request.goal, 
            request.days_per_week, 
            request.equipment, 
            injuries
        )
        
        # Build Exercise Inventory
        inventory = self.exercise_service.get_filtered_exercises(equipment=request.equipment)
        inventory_str = json.dumps(inventory, indent=2)

        prompt = f"""
You are an elite, science-based strength and conditioning coach. 
Your task is to build a {request.days_per_week}-day training program for a {request.goal} goal.

### TARGET VOLUME SETTINGS (Hit these exactly):
- Sets per exercise: {volume['sets_per_exercise']}
- Exercises per session: {volume['exercises_per_session']}
- Rep range: {volume['rep_range']}
- Rest between sets: {volume['rest_between_sets_seconds']} seconds

### SPORTS SCIENCE CONTEXT (Follow this strictly):
{rag_context}

### AVAILABLE EXERCISE INVENTORY:
You MUST ONLY choose exercises from this JSON inventory. You cannot invent new exercises.
{inventory_str}

Rules:
1. Every single session MUST have exactly {volume['exercises_per_session']} exercises.
2. Every single exercise MUST have exactly {volume['sets_per_exercise']} sets.
3. Every single exercise MUST have the rep range '{volume['rep_range']}'.
4. Every single exercise MUST have a rest period of {volume['rest_between_sets_seconds']} seconds.
5. Provide a specific science-backed tip from the RAG context in the notes for each exercise.
6. MANDATORY MUSCLE COVERAGE: You have exactly {volume['exercises_per_session'] * request.days_per_week} total exercise slots for the entire week. You MUST assign at least 1 exercise to EVERY single major muscle group (Chest, Back, Quads, Hamstrings, Shoulders, Biceps, Triceps, Calves, Core) BEFORE you assign a second exercise to any muscle group. Do not ignore Hamstrings or Calves!
7. EXACT NAMES ONLY: You MUST use the exact `name` string from the JSON inventory provided. Do not shorten or modify names (e.g., use "Barbell Bench Press", NOT "Bench Press").
"""

        messages = [
            {"role": "system", "content": "You are a professional strength and conditioning coach."},
            {"role": "user", "content": prompt}
        ]

        max_retries = 3
        program = None

        for attempt in range(max_retries):
            program = self.client.chat.completions.create(
                response_model=TrainingProgram,
                messages=messages
            )
            
            errors = self._validate_program(program, inventory, request.days_per_week)
            
            if not errors:
                print(f"Program passed strict validation on attempt {attempt + 1}!")
                break
            else:
                print(f"Validation failed on attempt {attempt + 1}. Errors: {errors}")
                if attempt < max_retries - 1:
                    messages.append({"role": "assistant", "content": program.model_dump_json()})
                    messages.append({"role": "user", "content": f"Your generated program failed validation with the following errors:\n" + "\n".join(errors) + "\nPlease correct your mistakes and regenerate the program."})
                else:
                    print("Max retries reached. Returning program with warnings.")

        return {
            "volume_settings": volume,
            "program": program.model_dump()
        }
