from fastapi import APIRouter, Depends

from app.models.planning import PlanRequest, PlanResponse
from app.services.planning_service import PlanningService

router = APIRouter()


def get_planning_service() -> PlanningService:
    return PlanningService()


@router.post("")
async def plan(request: PlanRequest, service: PlanningService = Depends(get_planning_service)) -> PlanResponse:
    return await service.run(request)
