from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import verify_clerk_token
from app.models.domain import User, GeneratedDiet, GeneratedProgram

router = APIRouter()

@router.get("/history")
def get_user_history(
    current_user: User = Depends(verify_clerk_token),
    db: Session = Depends(get_db)
):
    diets = db.query(GeneratedDiet).filter(GeneratedDiet.user_id == current_user.id).order_by(GeneratedDiet.created_at.desc()).all()
    programs = db.query(GeneratedProgram).filter(GeneratedProgram.user_id == current_user.id).order_by(GeneratedProgram.created_at.desc()).all()
    
    history = []
    
    for d in diets:
        history.append({
            "id": d.id,
            "type": "diet",
            "created_at": d.created_at,
            "data": d.diet_json
        })
        
    for p in programs:
        history.append({
            "id": p.id,
            "type": "program",
            "created_at": p.created_at,
            "data": p.program_json
        })
        
    # Sort combined history by created_at descending
    history.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {"history": history}
