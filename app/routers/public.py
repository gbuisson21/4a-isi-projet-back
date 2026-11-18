from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Closure, Menu, MenuPublic, PlanningDay, Product, ProductPublic

router = APIRouter(prefix="/api", tags=["public"])

SessionDep = Annotated[Session, Depends(get_session)]

MAX_PLANNING_DAYS = 366  # évite qu'un client demande un planning de plusieurs années


@router.get("/menus", response_model=list[MenuPublic])
def list_menus(session: SessionDep, date: date | None = None):
    """Liste les menus actifs avec leurs produits.

    Avec `?date=YYYY-MM-DD`, ne renvoie que les menus disponibles ce jour-là.
    """
    query = select(Menu).where(Menu.active == True)  # noqa: E712
    if date is not None:
        query = query.where(Menu.start_date <= date, Menu.end_date >= date)
    menus = session.exec(query.order_by(Menu.id)).all()
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


@router.get("/planning", response_model=list[PlanningDay])
def get_planning(session: SessionDep, start_date: date | None = None, end_date: date | None = None):
    """Planning jour par jour : fermetures et menus disponibles.

    Par défaut : la semaine en cours, du lundi au dimanche.
    """
    if start_date is None:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # lundi de la semaine
    if end_date is None:
        end_date = start_date + timedelta(days=6)
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")
    if (end_date - start_date).days >= MAX_PLANNING_DAYS:
        raise HTTPException(status_code=400, detail=f"Planning cannot exceed {MAX_PLANNING_DAYS} days")

    # 2 requêtes au total, puis on répartit en mémoire jour par jour
    closures = session.exec(
        select(Closure).where(Closure.closing_date >= start_date, Closure.closing_date <= end_date)
    ).all()
    closure_by_day = {c.closing_date: c for c in closures}

    menus = session.exec(
        select(Menu)
        .where(Menu.active == True, Menu.start_date <= end_date, Menu.end_date >= start_date)  # noqa: E712
        .order_by(Menu.id)
    ).all()
    menus_public = [(m, MenuPublic.from_db(m)) for m in menus]

    planning = []
    day = start_date
    while day <= end_date:
        closure = closure_by_day.get(day)
        planning.append(PlanningDay(
            date=day,
            is_closed=closure is not None,
            closure_reason=closure.reason if closure else None,
            menus=[] if closure else [mp for m, mp in menus_public if m.start_date <= day <= m.end_date],
        ))
        day += timedelta(days=1)
    return planning
