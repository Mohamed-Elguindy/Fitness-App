from fastapi import APIRouter, Depends
from app.models.schemas import TrainingProgramRequest
from app.services.program_service import ProgramService
from app.api.dependencies import get_program_service

router = APIRouter()

@router.post("/training-program")
def training_program(request: TrainingProgramRequest, program_service: ProgramService = Depends(get_program_service)):
    result = program_service.build_training_program(request)
    return result
