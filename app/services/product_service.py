from app.dao.product_dao import ProductDao


class ProductService:
    def __init__(self, dao: ProductDao):
        self.dao = dao

    def get_all(self, page: int, size: int):
        return self.dao.get_all(page, size)

    def get_by_id(self, product_id: int):
        return self.dao.get_by_id(product_id)
