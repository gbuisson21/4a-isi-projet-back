from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Menu, MenuPublic

router = APIRouter(prefix="/api", tags=["public"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/menus", response_model=list[MenuPublic])
def list_menus(session: SessionDep):
    """Liste les menus actifs avec leurs produits."""
    menus = session.exec(select(Menu).where(Menu.active == True).order_by(Menu.id)).all()  # noqa: E712
    return [MenuPublic.from_db(menu) for menu in menus]


@router.get("/menus/{menu_id}", response_model=MenuPublic)
def get_menu(menu_id: int, session: SessionDep):
    """Détail d'un menu."""
    menu = session.get(Menu, menu_id)
    if menu is None or not menu.active:
        raise HTTPException(status_code=404, detail="Menu not found")
    return MenuPublic.from_db(menu)
