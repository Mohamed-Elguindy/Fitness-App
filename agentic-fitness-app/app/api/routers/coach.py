from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.schemas import CoachRequest
from app.services.rag_service import RAGService
from app.api.dependencies import get_rag_service

router = APIRouter()

@router.post("/coach")
def coach(request: CoachRequest, rag_service: RAGService = Depends(get_rag_service)):
    try:
        prompt = request.query
        if request.user_context:
            prompt = f"User's Current Plan Context:\n{request.user_context}\n\nUser Question: {request.query}"
        
        response = rag_service.ask_coach(prompt)
        return {"response": response}
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return JSONResponse(status_code=429, content={"response": "⚠️ API rate limit reached. Please wait 30-60 seconds and try again."})
        return JSONResponse(status_code=500, content={"response": f"⚠️ Server error: {error_msg[:200]}"})
