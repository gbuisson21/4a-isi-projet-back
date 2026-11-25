from app.dao.product_dao import ProductDao
from app.models import ProductInput, ProductPublic, ProductUpdateInput, ProductStockUpdateInput


class ProductService:
    def __init__(self, dao: ProductDao):
        self.__dao = dao

    def get_all(self, page: int, size: int):
        return self.__dao.get_all(page, size)

    def get_by_id(self, product_id: int):
        return self.__dao.get_by_id(product_id)

    def create_product(self, product: ProductInput) -> ProductPublic:
        return self.__dao.create_product(product)

    def update_product(self, id_product: int, product: ProductUpdateInput):
        return self.__dao.update_product(id_product, product)

    def delete_product(self, product_id: int):
        return self.__dao.delete_product(product_id)

    def update_stock(self, product_id: int, product_stock: ProductStockUpdateInput):
        return self.__dao.update_stock(product_id, product_stock)
