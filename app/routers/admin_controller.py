from fastapi import APIRouter

from app.dependency import ProductServiceDep
from app.models import ProductPublic, ProductInput, ProductUpdateInput

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/products", response_model=ProductPublic, status_code=201)
def create_product(product: ProductInput, product_service: ProductServiceDep):
    return product_service.create_product(product)


@router.put("/products/{id_product}", response_model=ProductPublic, status_code=200)
def update_product(id_product: int, product: ProductUpdateInput, product_service: ProductServiceDep):
    return product_service.update_product(id_product, product)