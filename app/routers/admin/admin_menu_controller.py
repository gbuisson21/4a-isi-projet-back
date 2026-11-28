from fastapi import APIRouter, Depends

from app.dependency import MenuServiceDep, get_token_data
from app.models import MenuPublic, MenuInput, MenuUpdateInput, TokenData

router = APIRouter(prefix="/api/admin/menus", tags=["admin", "menus"])


@router.post("", response_model=MenuPublic, status_code=201)
def create_menu(menu: MenuInput, menu_service: MenuServiceDep, token_data: TokenData = Depends(get_token_data)):
    return menu_service.create_menu(menu, token_data)


@router.put("/{menu_id}", response_model=MenuPublic)
def update_menu(menu_id: int, menu: MenuUpdateInput, menu_service: MenuServiceDep,
                token_data: TokenData = Depends(get_token_data)):
    return menu_service.update_menu(menu_id, menu, token_data)


@router.delete("/{menu_id}", response_model=bool)
def delete_menu(menu_id: int, menu_service: MenuServiceDep, token_data: TokenData = Depends(get_token_data)):
    return menu_service.delete_menu(menu_id, token_data)
