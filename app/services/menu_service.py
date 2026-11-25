from datetime import date

from sqlmodel import Session

from app.dao.menu_dao import MenuDAO
from app.models import MenuInput, MenuUpdateInput


class MenuService:
    def __init__(self, dao: MenuDAO):
        self.__dao = dao

    def get_by_date(self, date: date, page: int, size: int):
        return self.__dao.get_by_date(date, page, size)

    def get_by_id(self, menu_id: int):
        return self.__dao.get_by_id(menu_id)

    def create_menu(self, menu: MenuInput):
        return self.__dao.create_menu(menu)

    def update_menu(self, menu_id: int, menu: MenuUpdateInput):
        return self.__dao.update_menu(menu_id, menu)
