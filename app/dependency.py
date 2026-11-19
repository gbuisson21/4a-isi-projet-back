from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.dao.menu_dao import MenuDAO
from app.database import db
from app.services.menu_service import MenuService

SessionDep = Annotated[Session, Depends(db.get_session)]


def get_menu_dao(session: SessionDep) -> MenuDAO:
    return MenuDAO(session)


def get_menu_service(session: SessionDep) -> MenuService:
    return MenuService(get_menu_dao(session), session)


MenuDAODep = Annotated[MenuDAO, Depends(get_menu_dao)]
MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]