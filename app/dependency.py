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
from app.services.hash_service import HashService
from app.services.token_service import TokenService

from app.dao.user_dao import UserDao
from app.services.user_service import UserService

SessionDep = Annotated[Session, Depends(db.get_session)]


def get_menu_dao(session: SessionDep) -> MenuDAO:
    return MenuDAO(session)


def get_menu_service(session: SessionDep) -> MenuService:
    return MenuService(get_menu_dao(session), session)


def get_product_dao(session: SessionDep) -> ProductDao:
    return ProductDao(session)


def get_product_service(session: SessionDep) -> ProductService:
    return ProductService(get_product_dao(session))


def get_planning_dao(session: SessionDep) -> PlanningDao:
    return PlanningDao(session, get_menu_dao(session))


def get_planning_service(session: SessionDep) -> PlanningService:
    return PlanningService(get_planning_dao(session))

def get_token_service() -> TokenService:
    return TokenService()

def get_user_dao(session: SessionDep,) -> UserDao:
    return UserDao(session)

def get_user_service(session: SessionDep) -> UserService:
    return UserService(dao=get_user_dao(session=session),token_service=get_token_service(), hash_service=get_hash_service())


def get_hash_service() -> HashService:
    return HashService()


MenuDAODep = Annotated[MenuDAO, Depends(get_menu_dao)]
MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]

ProductDaoDep = Annotated[ProductDao, Depends(get_product_dao)]
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]

PlanningDaoDep = Annotated[PlanningDao, Depends(get_planning_dao)]
PlanningServiceDep = Annotated[PlanningService, Depends(get_planning_service)]

TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]

UserDaoDep = Annotated[UserDao, Depends(get_user_dao)]

UserServiceDep = Annotated[UserService, Depends(get_user_service)]

HashServiceDep = Annotated[HashService, Depends(get_hash_service)]




