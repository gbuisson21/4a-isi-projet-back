from typing import Annotated

from fastapi import HTTPException, Depends
from sqlmodel import select, Session
from datetime import date

from app.database import db
from app.models import Menu, MenuPublic

SessionDep = Annotated[Session, Depends(db.get_session())]


class MenuDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_by_date(self, date: date, page: int, size: int) -> list[MenuPublic]:
        query = select(Menu).where(Menu.active == True)  # noqa: E712
        query = query.where(Menu.start_date <= date, Menu.end_date >= date).limit(size).offset(size * page)

        menus = self.session.exec(query.order_by(Menu.id)).all()
        return [MenuPublic.from_db(menu) for menu in menus]

    def get_by_id(self, menu_id: int) -> MenuPublic:
        """Détail d'un menu."""
        menu = self.session.get(Menu, menu_id)
        if menu is None or not menu.active:
            raise HTTPException(status_code=404, detail="Menu not found")
        return MenuPublic.from_db(menu)

    def get_active_overlapping(self, start_date: date, end_date: date) -> list[Menu]:
        query = select(Menu).where(Menu.active.is_(True), Menu.start_date <= end_date,
                                   Menu.end_date >= start_date).order_by(Menu.id)

        menus = self.session.exec(query).all()
        return menus