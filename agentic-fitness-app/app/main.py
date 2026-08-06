from fastapi import FastAPI
from app.api.routers import coach, diet, program

app = FastAPI(title="AI Fitness Coach API", description="SOLID Architected Backend for Fitness App")

app.include_router(coach.router, tags=["Coach"])
app.include_router(diet.router, tags=["Diet"])
app.include_router(program.router, tags=["Program"])
