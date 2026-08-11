from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
from app.models.schemas import DietPlanRequest
from app.services.diet_service import DietService
from app.api.dependencies import get_diet_service, verify_clerk_token
from app.models.domain import User

router = APIRouter()

@router.post("/diet-plan")
def diet_plan(request: DietPlanRequest, diet_service: DietService = Depends(get_diet_service)):
    result = diet_service.build_diet_plan(request)
    return result

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import User, GeneratedDiet

@router.post("/stream-diet-plan")
def stream_diet_plan(
    request: DietPlanRequest, 
    diet_service: DietService = Depends(get_diet_service),
    current_user: User = Depends(verify_clerk_token),
    db: Session = Depends(get_db)
):
    def event_generator():
        for update in diet_service.stream_diet_plan(request):
            if "result" in update:
                # Save the final result to the database!
                try:
                    plan = GeneratedDiet(
                        user_id=current_user.id,
                        diet_json=update["result"]
                    )
                    db.add(plan)
                    db.commit()
                    print(f"Saved diet plan for user {current_user.id}")
                except Exception as e:
                    print(f"Error saving diet to DB: {e}")
                    db.rollback()
            
            yield f"data: {json.dumps(update)}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
