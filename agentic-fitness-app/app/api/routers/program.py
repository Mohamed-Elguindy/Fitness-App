from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
from app.models.schemas import TrainingProgramRequest
from app.services.program_service import ProgramService
from app.api.dependencies import get_program_service, verify_clerk_token
from app.models.domain import User

router = APIRouter()

@router.post("/training-program")
def training_program(request: TrainingProgramRequest, program_service: ProgramService = Depends(get_program_service)):
    result = program_service.build_training_program(request)
    return result

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import User, GeneratedProgram

@router.post("/stream-training-program")
def stream_training_program(
    request: TrainingProgramRequest, 
    program_service: ProgramService = Depends(get_program_service),
    current_user: User = Depends(verify_clerk_token),
    db: Session = Depends(get_db)
):
    def event_generator():
        for update in program_service.stream_training_program(request):
            if "result" in update:
                # Save the final result to the database!
                try:
                    plan = GeneratedProgram(
                        user_id=current_user.clerk_id,
                        program_json=update["result"]
                    )
                    db.add(plan)
                    db.commit()
                    print(f"Saved training program for user {current_user.clerk_id}")
                except Exception as e:
                    print(f"Error saving program to DB: {e}")
                    db.rollback()
            
            yield f"data: {json.dumps(update)}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
