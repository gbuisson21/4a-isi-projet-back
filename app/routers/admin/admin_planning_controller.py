from fastapi import APIRouter, Depends

from app.dependency import PlanningServiceDep, get_token_data
from app.models import ClosureInput, ClosurePublic, TokenData

router = APIRouter(prefix="/api/admin/planning", tags=["admin", "planning"])


@router.post("", response_model=ClosurePublic, status_code=201)
def create_closure(closure: ClosureInput, planning_service: PlanningServiceDep,
                   token_data: TokenData = Depends(get_token_data)):
    return planning_service.create_closure(closure, token_data)


@router.delete("/{closure_id}", response_model=bool, status_code=200)
def delete_closure(closure_id: int, planning_service: PlanningServiceDep,
                   token_data: TokenData = Depends(get_token_data)):
    return planning_service.delete_closure(closure_id, token_data)
