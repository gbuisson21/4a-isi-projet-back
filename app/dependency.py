from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.dao.menu_dao import MenuDAO
from app.dao.planning_dao import PlanningDao
from app.dao.product_dao import ProductDao
from app.database import db
from app.services.menu_service import MenuService
from app.services.planning_service import PlanningService
from app.services.product_service import ProductService

SessionDep = Annotated[Session, Depends(db.get_session)]


def get_menu_dao(session: SessionDep) -> MenuDAO:
    return MenuDAO(session, get_product_dao(session))


def get_menu_service(session: SessionDep) -> MenuService:
    return MenuService(get_menu_dao(session))


def get_product_dao(session: SessionDep) -> ProductDao:
    return ProductDao(session)


def get_product_service(session: SessionDep) -> ProductService:
    return ProductService(get_product_dao(session))


def get_planning_dao(session: SessionDep) -> PlanningDao:
    return PlanningDao(session, get_menu_dao(session))


def get_planning_service(session: SessionDep) -> PlanningService:
    return PlanningService(get_planning_dao(session))


MenuDAODep = Annotated[MenuDAO, Depends(get_menu_dao)]
MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]

ProductDaoDep = Annotated[ProductDao, Depends(get_product_dao)]
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]

PlanningDaoDep = Annotated[PlanningDao, Depends(get_planning_dao)]
PlanningServiceDep = Annotated[PlanningService, Depends(get_planning_service)]
