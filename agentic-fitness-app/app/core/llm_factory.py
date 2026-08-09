import google.generativeai as genai
from app.core.config import settings

def get_gemini_client():
    """Factory function to get a configured Gemini client."""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel('gemini-3.6-flash')
