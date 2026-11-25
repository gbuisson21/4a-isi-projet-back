from fastapi import APIRouter

from app.dependency import ProductServiceDep
from app.models import ProductPublic, ProductInput, ProductUpdateInput, ProductStockUpdateInput

router = APIRouter(prefix="/api/admin/products", tags=["admin", "products"])


@router.post("", response_model=ProductPublic, status_code=201)
def create_product(product: ProductInput, product_service: ProductServiceDep):
    return product_service.create_product(product)


@router.put("/{id_product}", response_model=ProductPublic, status_code=200)
def update_product(id_product: int, product: ProductUpdateInput, product_service: ProductServiceDep):
    return product_service.update_product(id_product, product)


@router.delete("/{product_id}", status_code=200)
def delete_product(product_id: int, product_service: ProductServiceDep):
    return product_service.delete_product(product_id)


@router.put("/{product_id}/stock", response_model=ProductPublic, status_code=200)
def update_stock_product(product_id: int, product_stock: ProductStockUpdateInput, product_service: ProductServiceDep):
    return product_service.update_stock(product_id, product_stock)
