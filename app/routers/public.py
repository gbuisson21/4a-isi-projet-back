from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Menu, MenuPublic, Product, ProductPublic

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


@router.get("/products", response_model=list[ProductPublic])
def list_products(session: SessionDep):
    """Liste les produits actifs avec leur stock."""
    products = session.exec(select(Product).where(Product.active == True).order_by(Product.id)).all()  # noqa: E712
    return [ProductPublic.from_db(product) for product in products]


@router.get("/products/{product_id}", response_model=ProductPublic)
def get_product(product_id: int, session: SessionDep):
    """Détail d'un produit."""
    product = session.get(Product, product_id)
    if product is None or not product.active:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductPublic.from_db(product)
