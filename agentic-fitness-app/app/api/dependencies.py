from functools import lru_cache
import google.generativeai as genai
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import User
from typing import Optional
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

def verify_clerk_token(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Verifies the Clerk JWT token.
    For local development, if authorization header is missing or simple, 
    we fallback to a test user. Once Next.js is configured, we will enforce PyJWT decoding.
    """
    if not authorization or not authorization.startswith("Bearer "):
        print(f"Missing or invalid auth header: {authorization}")
        # Dev fallback: Return a dummy user or raise 401 if strict
        clerk_id = "test_clerk_id_123"
    else:
        token = authorization.split("Bearer ")[1]
        try:
            import base64
            import json
            # Decode the token payload (second part of JWT) without verifying
            payload_b64 = token.split(".")[1]
            # Add padding if necessary
            payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
            decoded = json.loads(base64.b64decode(payload_b64).decode("utf-8"))
            clerk_id = decoded.get("sub", "test_clerk_id_123")
            print(f"Decoded clerk_id from JWT: {clerk_id}")
        except Exception as e:
            # Fallback if decode fails
            print(f"Failed to decode JWT: {e}")
            clerk_id = token

    # Check if user exists in Neon DB, if not, create them
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
