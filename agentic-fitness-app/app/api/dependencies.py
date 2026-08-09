from functools import lru_cache
import google.generativeai as genai
from app.core.llm_factory import get_gemini_client
from app.services.rag_service import RAGService
from app.services.diet_service import DietService
from app.services.program_service import ProgramService
from app.services.exercise_service import ExerciseService
from app.services.meal_service import MealService

@lru_cache
def get_llm_client() -> genai.GenerativeModel:
    """Provides a singleton Gemini client instance."""
    return get_gemini_client()

@lru_cache
def get_rag_service() -> RAGService:
    """Provides a singleton RAGService instance."""
    return RAGService()

@lru_cache
def get_diet_service() -> DietService:
    """Provides a singleton DietService instance."""
    return DietService(get_llm_client())

@lru_cache
def get_program_service() -> ProgramService:
    """Provides a singleton ProgramService instance."""
    return ProgramService(get_llm_client())

@lru_cache
def get_exercise_service() -> ExerciseService:
    """Provides a singleton ExerciseService instance."""
    return ExerciseService()

@lru_cache
def get_meal_service() -> MealService:
    """Provides a singleton MealService instance."""
    return MealService()
