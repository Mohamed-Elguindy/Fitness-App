from pydantic import BaseModel
from typing import List, Optional

class CoachRequest(BaseModel):
    query: str
    user_context: Optional[str] = None

class DietPlanRequest(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    gender: str
    activity_level: str
    goal: str
    intensity: str = "moderate"
    meals_per_day: int = 3
    budget: str = "moderate"

class TrainingProgramRequest(BaseModel):
    available_minutes: int
    goal: str
    days_per_week: int
    equipment: str = "gym"
    injuries: Optional[str] = None

# --- LLM Output Schemas for Instructor ---

class MealSelection(BaseModel):
    meal_name: str
    target_calories: float
    meal_time: str

class DietPlan(BaseModel):
    meals: List[MealSelection]

class ExerciseSelection(BaseModel):
    exercise_name: str
    sets: int
    reps: str
    rest_seconds: int
    notes: str

class Session(BaseModel):
    day_name: str
    focus_muscles: List[str]
    exercises: List[ExerciseSelection]

class TrainingProgram(BaseModel):
    sessions: List[Session]