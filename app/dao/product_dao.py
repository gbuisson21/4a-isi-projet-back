from fastapi import HTTPException
from sqlmodel import select, Session

from app.models import Product, ProductPublic


class ProductDao:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, page: int = 0, size: int = 15):
        """Liste les produits actifs avec leur stock."""
        products = self.session.exec(
            select(Product).where(Product.active == True).limit(size).offset(size * page).order_by(
                Product.id)).all()  # noqa: E712
        return [ProductPublic.from_db(product) for product in products]

    def get_by_id(self, product_id: int):
        """Détail d'un produit."""
        product = self.session.get(Product, product_id)
        if product is None or not product.active:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductPublic.from_db(product)
