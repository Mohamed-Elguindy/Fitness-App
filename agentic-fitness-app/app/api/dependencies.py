from functools import lru_cache
from groq import Groq
from app.core.llm_factory import get_groq_client
from app.services.rag_service import RAGService
from app.services.diet_service import DietService
from app.services.program_service import ProgramService

@lru_cache
def get_llm_client() -> Groq:
    """Provides a singleton Groq client instance."""
    return get_groq_client()

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
