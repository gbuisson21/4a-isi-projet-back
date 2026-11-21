from datetime import date

from app.dao.planning_dao import PlanningDao


class PlanningService:
    def __init__(self, dao: PlanningDao):
        self.dao = dao

    def get_planning(self, start_date: date, end_date: date):
        return self.dao.get_planning(start_date, end_date)
