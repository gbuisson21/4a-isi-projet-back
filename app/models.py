"""Modèles SQLModel : correspondent aux tables de 4a-isi-projet-db/tables.sql."""
from datetime import date

from sqlmodel import Field, Relationship, SQLModel
from websockets import InvalidParameterValue


# ---------- Tables ----------

class MenuItem(SQLModel, table=True):
    """Table de liaison menus <-> products."""
    __tablename__ = "menu_items"

    id: int | None = Field(default=None, primary_key=True)
    menu_id: int = Field(foreign_key="menus.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = 1


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    price_cents: int
    stock: int
    active: bool = True


class Menu(SQLModel, table=True):
    __tablename__ = "menus"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    price_cents: int
    start_date: date
    end_date: date
    active: bool = True

    products: list[Product] = Relationship(link_model=MenuItem)


class Closure(SQLModel, table=True):
    __tablename__ = "closings"

    id: int | None = Field(default=None, primary_key=True)
    closing_date: date = Field(unique=True)
    reason: str | None = None


# ---------- Modèles de réponse (format d'API.md, prix en euros) ----------

class ProductPublic(SQLModel):
    id: int
    name: str
    price: float
    stock: int

    @classmethod
    def from_db(cls, product: Product) -> "ProductPublic":
        return cls(id=product.id, name=product.name,
                   price=product.price_cents / 100, stock=product.stock)


class MenuPublic(SQLModel):
    id: int
    name: str
    price: float
    start_date: date
    end_date: date
    products: list[ProductPublic]

    @classmethod
    def from_db(cls, menu: Menu) -> "MenuPublic":
        return cls(id=menu.id, name=menu.name, price=menu.price_cents / 100,
                   start_date=menu.start_date, end_date=menu.end_date,
                   products=[ProductPublic.from_db(p) for p in menu.products])


class PlanningDay(SQLModel):
    date: date
    is_closed: bool
    closure_reason: str | None
    menus: list[MenuPublic]


# ---------- Modèles d'entrée (format d'API.md, prix en euros) ----------

class ProductInput(SQLModel):
    name: str
    price: float
    stock: int


class ProductUpdateInput(SQLModel):
    name: str | None
    price: float | None

    def to_db_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True)
        if "price" in data:
            data["price_cents"] = round(data.pop("price") * 100)
        return data


class ProductStockUpdateInput(SQLModel):
    stock: int

    def to_db_dict(self):
        return {"stock": self.stock}


class MenuInput(SQLModel):
    name: str
    price: float
    start_date: date
    end_date: date
    product_ids: list[int]

