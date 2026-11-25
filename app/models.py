"""Modèles SQLModel : correspondent aux tables de 4a-isi-projet-db/tables.sql."""
from datetime import date

from pydantic import field_validator, model_validator
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


class ClosurePublic(SQLModel):
    id: int
    closure_date: date
    reason: str | None = None

    @classmethod
    def from_db(self, closure: Closure) -> "ClosurePublic":
        return self(
            id=closure.id,
            closure_date=closure.closing_date,
            reason=closure.reason)


# ---------- Modèles d'entrée (format d'API.md, prix en euros) ----------

class ProductInput(SQLModel):
    name: str
    price: float
    stock: int = 0

    @field_validator("price")
    @classmethod
    def price_cents_validator(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("stock")
    @classmethod
    def stock_validator(cls, v):
        if v < 0:
            raise ValueError("Stock must be greater than 0")
        return v

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        return v


class ProductUpdateInput(SQLModel):
    name: str | None = None
    price: float | None = None

    def to_db_dict(self) -> dict:
        data = self.model_dump(exclude_unset=True)
        if "price" in data:
            data["price_cents"] = round(data.pop("price") * 100)
        return data

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v):
        if v is None: return v
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        return v

    @field_validator("price")
    @classmethod
    def price_cents_validator(cls, v):
        if v is None: return v
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ProductStockUpdateInput(SQLModel):
    stock: int

    def to_db_dict(self):
        return {"stock": self.stock}

    @field_validator("stock")
    @classmethod
    def stock_validator(cls, v):
        if v < 0:
            raise ValueError("Stock must be greater than 0")
        return v


class MenuInput(SQLModel):
    name: str
    price: float
    start_date: date
    end_date: date
    product_ids: list[int]

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        return v

    @field_validator("price")
    @classmethod
    def price_cents_validator(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("product_ids")
    @classmethod
    def product_ids_validator(cls, v):
        if len(v) < 1:
            raise ValueError("There must be at least one product in the menu")
        return v

    @model_validator(mode="after")
    def date_validator(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
        return self


class MenuUpdateInput(SQLModel):
    name: str | None = None
    price: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    product_ids: list[int] | None = None

    def to_db_dict(self):
        data = self.model_dump(exclude_unset=True)
        if "price" in data:
            data["price_cents"] = round(data.pop("price") * 100)
        return data

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if v is None: return v
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        return v

    @field_validator("price")
    @classmethod
    def price_cents_validator(cls, v):
        if v is None: return v
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @model_validator(mode="after")
    def date_validator(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
        return self


class ClosureInput(SQLModel):
    date: str
    reason: str | None

    @field_validator("closure_date")
    @classmethod
    def closure_date_validator(cls, v):
        if date.fromisoformat(v.strip()) is None:
            raise ValueError("Closure date must be in YYYY-MM-DD format")
        return v.strip()
