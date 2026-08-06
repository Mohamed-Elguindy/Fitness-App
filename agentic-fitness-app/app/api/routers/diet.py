from fastapi import APIRouter, Depends
from app.models.schemas import DietPlanRequest
from app.services.diet_service import DietService
from app.api.dependencies import get_diet_service

router = APIRouter()

@router.post("/diet-plan")
def diet_plan(request: DietPlanRequest, diet_service: DietService = Depends(get_diet_service)):
    result = diet_service.build_diet_plan(request)
    return result
