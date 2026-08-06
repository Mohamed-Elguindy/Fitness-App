from fastapi import APIRouter, Depends
from app.models.schemas import CoachRequest
from app.services.rag_service import RAGService
from app.api.dependencies import get_rag_service

router = APIRouter()

@router.post("/coach")
def coach(request: CoachRequest, rag_service: RAGService = Depends(get_rag_service)):
    prompt = request.query
    if request.user_context:
        prompt = f"User's Current Plan Context:\n{request.user_context}\n\nUser Question: {request.query}"
    
    response = rag_service.ask_coach(prompt)
    return {"response": response}
