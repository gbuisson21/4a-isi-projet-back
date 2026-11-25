from datetime import date, timedelta
from fastapi import HTTPException
from sqlmodel import Session, select

from app.dao.menu_dao import MenuDAO
from app.models import MenuPublic, PlanningDay, Closure, ClosureInput, ClosurePublic

MAX_PLANNING_DAYS = 366  # évite qu'un client demande un planning de plusieurs années


class PlanningDao:
    def __init__(self, session: Session, menu_dao: MenuDAO):
        self.__session = session
        self.__menu_dao = menu_dao

    def get_planning(self, start_date: date, end_date: date):
        """Planning jour par jour : fermetures et menus disponibles.

        Par défaut : la semaine en cours, du lundi au dimanche.
        """

        closures = self.__session.exec(
            select(Closure).where(Closure.closing_date >= start_date, Closure.closing_date <= end_date)
        ).all()
        closure_by_day = {c.closing_date: c for c in closures}

        menus = [
            (m, MenuPublic.from_db(m))
            for m in self.__menu_dao.get_active_overlapping(start_date, end_date)
        ]

        planning = []
        day = start_date
        while day <= end_date:
            closure = closure_by_day.get(day)
            planning.append(PlanningDay(
                date=day,
                is_closed=closure is not None,
                closure_reason=closure.reason if closure else None,
                menus=[] if closure else [mp for m, mp in menus if m.start_date <= day <= m.end_date],
            ))
            day += timedelta(days=1)
        return planning

    def create_closure(self, closure: ClosureInput) -> ClosurePublic:
        closure_this_day_query = select(Closure).where(Closure.closing_date == date.fromisoformat(closure.date))
        closure_this_day = self.__session.get(closure_this_day_query)

        if closure_this_day:
            raise HTTPException(status_code=409, detail="Day already closed")

        closure_with_id = Closure(closing_date=date.fromisoformat(closure.date),
                                  reason=closure.reason if closure.reason else None)

        self.__session.add(closure_with_id)
        self.__session.commit()

        return ClosurePublic.from_db(closure_with_id)

    def delete_closure(self, closure_id: int):
        closure = self.__session.get(Closure, closure_id)
        if not closure:
            raise HTTPException(status_code=404, detail="Closure does not exist")

        self.__session.delete(closure)
        self.__session.commit()
        return True
