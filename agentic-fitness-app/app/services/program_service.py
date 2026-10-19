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

    # --- Public API Endpoints (The Headlines) ---

    def build_training_program(self, request: TrainingProgramRequest) -> dict:
        volume = self._calculate_training_volume(request)
        rag_context = self._get_rag_context(request)
        available_exercises = self._get_available_exercises(request.equipment)

        messages = self._create_initial_messages(request, volume, rag_context, available_exercises)
        program, errors = self._generate_valid_program(messages, available_exercises)

        return {
            "volume_settings": volume,
            "program": program.model_dump(),
            "validation_errors": errors
        }

    def stream_training_program(self, request: TrainingProgramRequest):
        yield {"status": "initializing coach core..."}

        yield {"status": "calculating optimal volume..."}
        volume = self._calculate_training_volume(request)

        yield {"status": "querying sports science literature..."}
        rag_context = self._get_rag_context(request)

        yield {"status": "building exercise inventory..."}
        available_exercises = self._get_available_exercises(request.equipment)

        messages = self._create_initial_messages(request, volume, rag_context, available_exercises)

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
            errors = self._validate_program(program, available_exercises)

            if not errors:
                yield {"status": "validation passed! finalising..."}
                break

            if attempt < max_retries - 1:
                yield {"status": "validation failed. recalculating..."}
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

    # --- Pipeline Helpers (Stepdown Order) ---

    def _calculate_training_volume(self, request: TrainingProgramRequest) -> dict:
        try:
            goal_enum = Goal(request.goal.lower())
        except ValueError:
            goal_enum = Goal.HYPERTROPHY
        return self.calculator.calculate_training_volume(request.available_minutes, goal_enum)

    def _get_rag_context(self, request: TrainingProgramRequest) -> str:
        injuries = request.injuries if request.injuries else "none"
        return self.rag_service.get_training_context(
            request.goal,
            request.days_per_week,
            request.equipment,
            injuries
        )

    def _get_available_exercises(self, equipment: str) -> list[dict]:
        return self.exercise_service.get_filtered_exercises(equipment=equipment)

    def _create_initial_messages(
        self,
        request: TrainingProgramRequest,
        volume: dict,
        rag_context: str,
        available_exercises: list[dict]
    ) -> list[dict]:
        available_exercises_json = json.dumps(available_exercises, indent=2)
        prompt = get_training_program_prompt(
            request.days_per_week,
            request.goal,
            volume,
            rag_context,
            available_exercises_json
        )
        return [
            {"role": "system", "content": get_training_system_prompt()},
            {"role": "user", "content": prompt}
        ]

    def _generate_valid_program(
        self, messages: list[dict], available_exercises: list[dict], max_retries: int = 3
    ) -> tuple[TrainingProgram, list[str]]:
        program = None
        errors = []

        for attempt in range(max_retries):
            program = self.client.chat.completions.create(
                response_model=TrainingProgram,
                messages=messages
            )
            errors = self._validate_program(program, available_exercises)

            if not errors:
                print(f"Program passed strict validation on attempt {attempt + 1}!")
                break

            print(f"Validation failed on attempt {attempt + 1}. Errors: {errors}")
            if attempt < max_retries - 1:
                messages.append({"role": "assistant", "content": program.model_dump_json()})
                messages.append({"role": "user", "content": get_validation_retry_prompt(errors)})
            else:
                print("Max retries reached. Returning program with warnings.")

        return program, errors

    # --- Validation Helpers ---

    def _validate_program(self, program: TrainingProgram, available_exercises: list[dict]) -> list[str]:
        allowed_exercises = {exercise["name"].lower(): exercise for exercise in available_exercises}
        return [
            *self._check_exercise_validity_and_uniqueness(program, allowed_exercises),
            *self._check_primary_muscle_coverage(program, allowed_exercises),
            *self._check_session_focus_alignment(program, allowed_exercises),
        ]

    def _check_exercise_validity_and_uniqueness(
        self, program: TrainingProgram, allowed_exercises: dict
    ) -> list[str]:
        errors = []
        used_exercises = set()

        for session in program.sessions:
            for exercise in session.exercises:
                exercise_name = exercise.exercise_name.lower()
                if exercise_name not in allowed_exercises:
                    errors.append(
                        f"Exercise '{exercise.exercise_name}' is not in the inventory. "
                        "You MUST pick EXACT names from the inventory provided."
                    )
                elif exercise_name in used_exercises:
                    errors.append(
                        f"You used '{exercise.exercise_name}' more than once in the program. "
                        "You must select a unique exercise for every single slot."
                    )
                else:
                    used_exercises.add(exercise_name)

        return errors

    def _check_primary_muscle_coverage(
        self, program: TrainingProgram, allowed_exercises: dict
    ) -> list[str]:
        hit_primary_muscles = set()

        for session in program.sessions:
            for exercise in session.exercises:
                exercise_name = exercise.exercise_name.lower()
                if exercise_name in allowed_exercises:
                    exercise_data = allowed_exercises[exercise_name]
                    if "primary_muscle" in exercise_data:
                        hit_primary_muscles.add(exercise_data["primary_muscle"].lower())

        targeted_muscles_text = " ".join(hit_primary_muscles)
        required_muscles = ["chest", "back", "quadriceps", "hamstrings", "shoulder", "bicep", "tricep", "calves"]
        missing = [
            muscle for muscle in required_muscles
            if muscle not in targeted_muscles_text and f"{muscle}s" not in targeted_muscles_text
        ]

        if missing:
            return [
                f"Your program forgot to include exercises that target: {', '.join(missing)} AS A PRIMARY MUSCLE. "
                "You must include at least one isolation or compound exercise where these are the PRIMARY focus."
            ]
        return []

    def _check_session_focus_alignment(
        self, program: TrainingProgram, allowed_exercises: dict
    ) -> list[str]:
        errors = []

        for session in program.sessions:
            focus_muscles_text = " ".join(session.focus_muscles).lower()
            for exercise in session.exercises:
                exercise_name = exercise.exercise_name.lower()
                if exercise_name in allowed_exercises:
                    primary_muscle = allowed_exercises[exercise_name].get("primary_muscle", "").lower()
                    if (
                        primary_muscle
                        and primary_muscle not in focus_muscles_text
                        and primary_muscle[:-1] not in focus_muscles_text
                    ):
                        errors.append(
                            f"In session '{session.day_name}', you included '{exercise.exercise_name}' "
                            f"(targets {primary_muscle}), but the focus muscles for this day are: "
                            f"{', '.join(session.focus_muscles)}. Please replace it with an exercise that matches the day's focus."
                        )

        return errors
