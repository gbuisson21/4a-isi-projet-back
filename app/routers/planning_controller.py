from datetime import date, timedelta

from fastapi import HTTPException, APIRouter

from app.dependency import PlanningServiceDep
from app.models import PlanningDay

MAX_PLANNING_DAYS = 366  # évite qu'un client demande un planning de plusieurs années

router = APIRouter(prefix="/api/", tags=["planning"])

@router.get("/planning", response_model=list[PlanningDay])
def get_planning(service: PlanningServiceDep, start_date: date | None = None, end_date: date | None = None):
    """Planning jour par jour : fermetures et menus disponibles.

    Par défaut : la semaine en cours, du lundi au dimanche.
    """
    if start_date is None:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # lundi de la semaine
    if end_date is None:
        end_date = start_date + timedelta(days=6)
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")
    if (end_date - start_date).days >= MAX_PLANNING_DAYS:
        raise HTTPException(status_code=400, detail=f"Planning cannot exceed {MAX_PLANNING_DAYS} days")

    return service.get_planning(start_date, end_date)
