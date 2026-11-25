from typing import Annotated

from fastapi import APIRouter

from app.dependency import PlanningServiceDep
from app.models import ClosureInput, ClosurePublic

router = APIRouter(prefix="/api/admin/planning", tags=["admin", "planning"])

@router.post("", response_model=ClosurePublic ,status_code=201)
def create_closure(closure: ClosureInput, planning_service: PlanningServiceDep):
    return planning_service.create_closure(closure)


@router.delete("/{closure_id}", response_model=bool, status_code=200)
def delete_closure(closure_id: int, planning_service: PlanningServiceDep):
    return planning_service.delete_closure(closure_id)
