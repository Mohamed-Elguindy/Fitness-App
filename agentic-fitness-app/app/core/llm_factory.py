from groq import Groq
from app.core.config import settings

def get_groq_client() -> Groq:
    """Factory function to get a configured Groq client."""
    return Groq(api_key=settings.GROQ_API_KEY)
