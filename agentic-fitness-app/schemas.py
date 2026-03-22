from pydantic import BaseModel

class CoachRequest(BaseModel):
    query: str

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