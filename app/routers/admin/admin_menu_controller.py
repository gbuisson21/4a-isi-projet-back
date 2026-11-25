from fastapi import APIRouter

from app.dependency import MenuServiceDep
from app.models import MenuPublic, MenuInput, MenuUpdateInput

router = APIRouter(prefix="/api/admin/menus", tags=["admin", "menus"])


@router.post("/", response_model=MenuPublic)
def create_menu(menu: MenuInput, menu_service: MenuServiceDep):
    return menu_service.create_menu(menu)


@router.put("/{menu_id}", response_model=MenuPublic)
def update_menu(menu_id: int, menu: MenuUpdateInput, menu_service: MenuServiceDep):
    return menu_service.update_menu(menu_id, menu)