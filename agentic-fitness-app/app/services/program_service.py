import json
import instructor
import google.generativeai as genai
from app.models.schemas import TrainingProgramRequest, TrainingProgram
from app.services.exercise_service import ExerciseService
from app.services.rag_service import RAGService
from app.utils.calculator import CalculatorService, Goal
from app.utils.prompts import get_training_program_prompt, get_training_system_prompt, get_validation_retry_prompt

class ProgramService:
    def __init__(self, llm_client: genai.GenerativeModel):
        self.client = instructor.from_gemini(client=llm_client, mode=instructor.Mode.GEMINI_JSON)
        self.exercise_service = ExerciseService()
        self.rag_service = RAGService()
        self.calculator = CalculatorService()

    def _validate_program(self, program: TrainingProgram, available_exercises: list, days_per_week: int) -> list[str]:
        errors = []
        allowed_exercises = {exercise["name"].lower(): exercise for exercise in available_exercises}
        
        # 1. Check for exact names and duplicates
        used_exercises = set()
        for session in program.sessions:
            for exercise in session.exercises:
                exercise_name = exercise.exercise_name.lower()
                if exercise_name not in allowed_exercises:
                    errors.append(f"Exercise '{exercise.exercise_name}' is not in the inventory. You MUST pick EXACT names from the inventory provided.")
                else:
                    if exercise_name in used_exercises:
                        errors.append(f"You used '{exercise.exercise_name}' more than once in the program. You must select a unique exercise for every single slot.")
                    used_exercises.add(exercise_name)
                    
        # 2. Check Primary Muscle Coverage
        hit_primary_muscles = set()
        for session in program.sessions:
            for exercise in session.exercises:
                exercise_name = exercise.exercise_name.lower()
                if exercise_name in allowed_exercises:
                    exercise_data = allowed_exercises[exercise_name]
                    if "primary_muscle" in exercise_data:
                        hit_primary_muscles.add(exercise_data["primary_muscle"].lower())
                        
        # Required macro groups must be hit as PRIMARY muscles
        targeted_muscles_text = " ".join(hit_primary_muscles)
        required = ["chest", "back", "quadriceps", "hamstrings", "shoulder", "bicep", "tricep", "calves"]
        missing = [required_muscle for required_muscle in required if required_muscle not in targeted_muscles_text and required_muscle + "s" not in targeted_muscles_text]
        
        if missing:
            errors.append(f"Your program forgot to include exercises that target: {', '.join(missing)} AS A PRIMARY MUSCLE. You must include at least one isolation or compound exercise where these are the PRIMARY focus.")

        # 3. Check that the primary muscles targeted align with the session's focus_muscles
        for session in program.sessions:
            focus_muscles_text = " ".join(session.focus_muscles).lower()
            for exercise in session.exercises:
                exercise_name = exercise.exercise_name.lower()
                if exercise_name in allowed_exercises:
                    primary_muscle = allowed_exercises[exercise_name].get("primary_muscle", "").lower()
                    if primary_muscle and primary_muscle not in focus_muscles_text and primary_muscle[:-1] not in focus_muscles_text:
                         errors.append(f"In session '{session.day_name}', you included '{exercise.exercise_name}' (targets {primary_muscle}), but the focus muscles for this day are: {', '.join(session.focus_muscles)}. Please replace it with an exercise that matches the day's focus.")

        return errors

    def build_training_program(self, request: TrainingProgramRequest) -> dict:
        try:
            goal_enum = Goal(request.goal.lower())
        except ValueError:
            goal_enum = Goal.HYPERTROPHY

        volume = self.calculator.calculate_training_volume(request.available_minutes, goal_enum)
        
        # Pull RAG Context
        injuries = request.injuries if request.injuries else "none"
        rag_context = self.rag_service.get_training_context(
            request.goal, 
            request.days_per_week, 
            request.equipment, 
            injuries
        )
        
        # Build Exercise Inventory
        available_exercises = self.exercise_service.get_filtered_exercises(equipment=request.equipment)
        available_exercises_json = json.dumps(available_exercises, indent=2)

        training_program_prompt = get_training_program_prompt(
            request.days_per_week,
            request.goal,
            volume,
            rag_context,
            available_exercises_json
        )

        messages = [
            {"role": "system", "content": get_training_system_prompt()},
            {"role": "user", "content": training_program_prompt}
        ]

        max_retries = 3
        program = None
        errors = []

        for attempt in range(max_retries):
            program = self.client.chat.completions.create(
                response_model=TrainingProgram,
                messages=messages
            )
            
            errors = self._validate_program(program, available_exercises, request.days_per_week)
            
            if not errors:
                print(f"Program passed strict validation on attempt {attempt + 1}!")
                break
            else:
                print(f"Validation failed on attempt {attempt + 1}. Errors: {errors}")
                if attempt < max_retries - 1:
                    messages.append({"role": "assistant", "content": program.model_dump_json()})
                    messages.append({"role": "user", "content": get_validation_retry_prompt(errors)})
                else:
                    print("Max retries reached. Returning program with warnings.")

        return {
            "volume_settings": volume,
            "program": program.model_dump(),
            "validation_errors": errors
        }

    def stream_training_program(self, request: TrainingProgramRequest):
        yield {"status": "initializing coach core..."}
        
        try:
            goal_enum = Goal(request.goal.lower())
        except ValueError:
            goal_enum = Goal.HYPERTROPHY

        yield {"status": "calculating optimal volume..."}
        volume = self.calculator.calculate_training_volume(request.available_minutes, goal_enum)
        
        yield {"status": "querying sports science literature..."}
        injuries = request.injuries if request.injuries else "none"
        rag_context = self.rag_service.get_training_context(
            request.goal, 
            request.days_per_week, 
            request.equipment, 
            injuries
        )
        
        yield {"status": "building exercise inventory..."}
        available_exercises = self.exercise_service.get_filtered_exercises(equipment=request.equipment)
        available_exercises_json = json.dumps(available_exercises, indent=2)

        training_program_prompt = get_training_program_prompt(
            request.days_per_week,
            request.goal,
            volume,
            rag_context,
            available_exercises_json
        )

        messages = [
            {"role": "system", "content": get_training_system_prompt()},
            {"role": "user", "content": training_program_prompt}
        ]

        max_retries = 3
        program = None
        errors = []

        for attempt in range(max_retries):
            yield {"status": f"generating macro split (attempt {attempt + 1})..."}
            program = self.client.chat.completions.create(
                response_model=TrainingProgram,
                messages=messages
            )
            
            yield {"status": "validating anatomical coverage..."}
            errors = self._validate_program(program, available_exercises, request.days_per_week)
            
            if not errors:
                yield {"status": "validation passed! finalising..."}
                break
            else:
                if attempt < max_retries - 1:
                    yield {"status": f"validation failed. recalculating..."}
                    messages.append({"role": "assistant", "content": program.model_dump_json()})
                    messages.append({"role": "user", "content": get_validation_retry_prompt(errors)})
                else:
                    yield {"status": "max retries reached. forcing output..."}

        yield {
            "result": {
                "volume_settings": volume,
                "program": program.model_dump(),
                "validation_errors": errors
            }
        }
