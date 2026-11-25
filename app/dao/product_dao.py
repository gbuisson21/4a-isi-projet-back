from fastapi import HTTPException
from sqlmodel import select, Session

from app.models import Product, ProductPublic, ProductInput, ProductUpdateInput


class ProductDao:
    def __init__(self, session: Session):
        self.__session = session

    def get_all(self, page: int = 0, size: int = 15):
        """Liste les produits actifs avec leur stock."""
        products = self.__session.exec(
            select(Product).where(Product.active == True).limit(size).offset(size * page).order_by(
                Product.id)).all()  # noqa: E712
        return [ProductPublic.from_db(product) for product in products]

    def get_by_id(self, product_id: int):
        """Détail d'un produit."""
        product = self.__session.get(Product, product_id)
        if product is None or not product.active:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductPublic.from_db(product)

    def create_product(self, product: ProductInput) -> ProductPublic:
        product_with_id = Product(name=product.name, price_cents=round(product.price*100), stock=product.stock)
        self.__session.add(product_with_id)
        self.__session.commit()

        return ProductPublic.from_db(product_with_id)

    def update_product(self, id_product: int, product: ProductUpdateInput):
        db_product = self.__session.get(Product, id_product)

        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        product_data = product.to_db_dict()

        db_product.sqlmodel_update(product_data)
        self.__session.add(db_product)
        self.__session.commit()
        self.__session.refresh(db_product)
        return ProductPublic.from_db(db_product)

    def delete_product(self, product_id: int):
        product = self.__session.get(Product, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        self.__session.delete(product)
        self.__session.commit()
        return True

