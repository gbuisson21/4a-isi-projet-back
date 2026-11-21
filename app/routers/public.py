from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import db
from app.models import Closure, Menu, MenuPublic, PlanningDay

router = APIRouter(prefix="/api", tags=["public"])

SessionDep = Annotated[Session, Depends(db.get_session)]

MAX_PLANNING_DAYS = 366  # évite qu'un client demande un planning de plusieurs années


@router.get("/planning", response_model=list[PlanningDay])
def get_planning(session: SessionDep, start_date: date | None = None, end_date: date | None = None):
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

    # 2 requêtes au total, puis on répartit en mémoire jour par jour
    closures = session.exec(
        select(Closure).where(Closure.closing_date >= start_date, Closure.closing_date <= end_date)
    ).all()
    closure_by_day = {c.closing_date: c for c in closures}

    menus = session.exec(
        select(Menu)
        .where(Menu.active == True, Menu.start_date <= end_date, Menu.end_date >= start_date)  # noqa: E712
        .order_by(Menu.id)
    ).all()
    menus_public = [(m, MenuPublic.from_db(m)) for m in menus]

    planning = []
    day = start_date
    while day <= end_date:
        closure = closure_by_day.get(day)
        planning.append(PlanningDay(
            date=day,
            is_closed=closure is not None,
            closure_reason=closure.reason if closure else None,
            menus=[] if closure else [mp for m, mp in menus_public if m.start_date <= day <= m.end_date],
        ))
        day += timedelta(days=1)
    return planning
