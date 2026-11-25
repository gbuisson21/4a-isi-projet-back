from datetime import date

from app.dao.planning_dao import PlanningDao
from app.models import ClosureInput


class PlanningService:
    def __init__(self, dao: PlanningDao):
        self.__dao = dao

    def get_planning(self, start_date: date, end_date: date):
        return self.__dao.get_planning(start_date, end_date)

    def create_closure(self, closure: ClosureInput):
        return self.__dao.create_closure(closure)
