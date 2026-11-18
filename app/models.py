"""Modèles SQLModel : correspondent aux tables de 4a-isi-projet-db/tables.sql."""
from sqlmodel import Field, Relationship, SQLModel


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
    active: bool = True

    products: list[Product] = Relationship(link_model=MenuItem)


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
    products: list[ProductPublic]

    @classmethod
    def from_db(cls, menu: Menu) -> "MenuPublic":
        return cls(id=menu.id, name=menu.name, price=menu.price_cents / 100,
                   products=[ProductPublic.from_db(p) for p in menu.products])
