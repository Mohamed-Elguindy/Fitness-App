from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import coach, diet, program, history

app = FastAPI(
    title="Agentic Fitness App",
    description="An AI-powered fitness application running locally",
    version="1.0.0"
)

# Add CORS Middleware for Next.js premium frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(coach.router, tags=["Coach"])
app.include_router(diet.router, tags=["Diet"])
app.include_router(program.router, tags=["Program"])
app.include_router(history.router, tags=["History"])
