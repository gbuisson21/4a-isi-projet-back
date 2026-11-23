from datetime import date

from fastapi import APIRouter

from app.dependency import MenuServiceDep
from app.models import MenuPublic

router = APIRouter(prefix="/api", tags=["menu"])

MAX_PLANNING_DAYS = 366  # évite qu'un client demande un planning de plusieurs années


@router.get("/menus", response_model=list[MenuPublic])
def list_menus(date: date, menu_service: MenuServiceDep, page: int = 0, size: int = 100):
    """Liste les menus actifs avec leurs produits.

    Avec `?date=YYYY-MM-DD`, ne renvoie que les menus disponibles ce jour-là.
    """
    return menu_service.get_by_date(date, page, size)


@router.get("/menus/{menu_id}", response_model=MenuPublic)
def get_menu(menu_id: int, menu_service: MenuServiceDep):
    """Détail d'un menu."""
    return menu_service.get_by_id(menu_id)
