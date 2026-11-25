from datetime import date

from fastapi import HTTPException, Depends
from sqlmodel import select, Session

from app.dao.product_dao import ProductDao
from app.models import Menu, MenuPublic, MenuInput, MenuUpdateInput

class MenuDAO:
    def __init__(self, session: Session, product_dao: ProductDao):
        self.__session = session
        self.__product_dao = product_dao

    def get_by_date(self, date: date, page: int, size: int) -> list[MenuPublic]:
        query = select(Menu).where(Menu.active == True)  # noqa: E712
        query = query.where(Menu.start_date <= date, Menu.end_date >= date).limit(size).offset(size * page)

        menus = self.__session.exec(query.order_by(Menu.id)).all()
        return [MenuPublic.from_db(menu) for menu in menus]

    def get_by_id(self, menu_id: int) -> MenuPublic:
        """Détail d'un menu."""
        menu = self.__session.get(Menu, menu_id)
        if menu is None or not menu.active:
            raise HTTPException(status_code=404, detail="Menu not found")
        return MenuPublic.from_db(menu)

    def get_active_overlapping(self, start_date: date, end_date: date) -> list[Menu]:
        query = select(Menu).where(Menu.active.is_(True), Menu.start_date <= end_date,
                                   Menu.end_date >= start_date).order_by(Menu.id)

        menus = self.__session.exec(query).all()
        return menus

    def create_menu(self, menu: MenuInput):
        products = [self.__product_dao.get_by_id(product_id) for product_id in menu.product_ids]
        menu_db = Menu(name=menu.name, products=products, start_date=menu.start_date, end_date=menu.end_date,
                       price_cents=round(menu.price * 100))

        self.__session.add(menu_db)
        self.__session.commit()
        return MenuPublic.from_db(menu_db)

    def update_menu(self, menu_id: int, menu: MenuUpdateInput):
        menu_db = self.__session.get(Menu, menu_id)

        if not menu_db:
            raise HTTPException(status_code=404, detail="Product not found")

        menu_data = menu.to_db_dict()

        if menu.product_ids:
            menu_data["products"] = [self.__product_dao.get_by_id(product_id) for product_id in menu.product_ids]

        menu_db.sqlmodel_update(menu_data)
        self.__session.add(menu_db)
        self.__session.commit()
        self.__session.refresh(menu_db)
        return MenuPublic.from_db(menu_db)

    def delete_menu(self, menu_id: int):
        menu = self.__session.get(Menu, menu_id)

        # TODO: Check for pending reservations

        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")

        self.__session.delete(menu)
        self.__session.commit()
        return True
