import code
from datetime import date

from fastapi import HTTPException

from app.dao.menu_dao import MenuDAO
from app.models import MenuInput, MenuUpdateInput, TokenData
from app.services.token_service import TokenService


class MenuService:
    def __init__(self, dao: MenuDAO, token_service: TokenService):
        self.__dao = dao
        self.__token_service = token_service

    def get_by_date(self, date: date, page: int, size: int):
        return self.__dao.get_by_date(date, page, size)

    def get_by_id(self, menu_id: int):
        return self.__dao.get_by_id(menu_id)

    def create_menu(self, menu: MenuInput, token: TokenData):
        if not self.__token_service.is_admin(token):
            return HTTPException(status_code=403, detail="Admin privilege required")

        return self.__dao.create_menu(menu)

    def update_menu(self, menu_id: int, menu: MenuUpdateInput, token: TokenData):
        if not self.__token_service.is_admin(token):
            return HTTPException(status_code=403, detail="Admin privilege required")

        return self.__dao.update_menu(menu_id, menu)

    def delete_menu(self, menu_id: int, token: TokenData):
        if not self.__token_service.is_admin(token):
            return HTTPException(status_code=403, detail="Admin privilege required")

        return self.__dao.delete_menu(menu_id)
