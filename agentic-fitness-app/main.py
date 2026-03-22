from fastapi import FastAPI
from ai_core import ask_coach
from program_builder import build_training_program
from schemas import CoachRequest, DietPlanRequest, TrainingProgramRequest
from diet_builder import build_diet_plan


app = FastAPI()

@app.post("/coach")
def coach(request: CoachRequest):
    response = ask_coach(request.query)
    return {"response": response}

@app.post("/diet-plan")
def diet_plan(request: DietPlanRequest):
    result = build_diet_plan(request)
    return result

@app.post("/training-program")
def training_program(request: TrainingProgramRequest):
    result = build_training_program(request)
    return result