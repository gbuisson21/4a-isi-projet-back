from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import db
from app.dependency import ProductServiceDep
from app.models import Product, ProductPublic

router = APIRouter(prefix="/api", tags=["public"])

MAX_PLANNING_DAYS = 366  # évite qu'un client demande un planning de plusieurs années


@router.get("/products", response_model=list[ProductPublic])
def list_products(service: ProductServiceDep, page: int = 0, size: int = 100):
    """Liste les produits actifs avec leur stock."""
    return service.get_all(page, size)


@router.get("/products/{product_id}", response_model=ProductPublic)
def get_product(product_id: int, service: ProductServiceDep):
    """Détail d'un produit."""
    return service.get_by_id(product_id)
