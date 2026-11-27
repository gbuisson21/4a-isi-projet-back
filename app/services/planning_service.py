from datetime import date

from fastapi import HTTPException

from app.dao.planning_dao import PlanningDao
from app.models import ClosureInput, TokenData
from app.services.token_service import TokenService


class PlanningService:
    def __init__(self, dao: PlanningDao, token_service: TokenService):
        self.__dao = dao
        self.__token_service = token_service

    def get_planning(self, start_date: date, end_date: date):
        return self.__dao.get_planning(start_date, end_date)

    def create_closure(self, closure: ClosureInput, token_data: TokenData):
        if not self.__token_service.is_admin(token_data):
            return HTTPException(status_code=403, detail="Admin privilege required")
        return self.__dao.create_closure(closure)

    def delete_closure(self, closure_id: int, token_data: TokenData):
        if not self.__token_service.is_admin(token_data):
            return HTTPException(status_code=403, detail="Admin privilege required")
        return self.__dao.delete_closure(closure_id)
