from datetime import date, timedelta

from sqlmodel import Session, select

from app.dao.menu_dao import MenuDAO
from app.models import MenuPublic, PlanningDay, Closure

MAX_PLANNING_DAYS = 366  # évite qu'un client demande un planning de plusieurs années


class PlanningDao:
    def __init__(self, session: Session, menu_dao: MenuDAO):
        self.session = session
        self.menu_dao = menu_dao

    def get_planning(self, start_date: date, end_date: date):
        """Planning jour par jour : fermetures et menus disponibles.

        Par défaut : la semaine en cours, du lundi au dimanche.
        """

        closures = self.session.exec(
            select(Closure).where(Closure.closing_date >= start_date, Closure.closing_date <= end_date)
        ).all()
        closure_by_day = {c.closing_date: c for c in closures}

        menus = [
            (m, MenuPublic.from_db(m))
            for m in self.menu_dao.get_active_overlapping(start_date, end_date)
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
