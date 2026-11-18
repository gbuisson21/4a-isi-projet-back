import sqlite3

from sqlalchemy import event
from sqlmodel import Session, create_engine

from app.config import DB_PATH, SQL_DIR

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_conn, _):
    # SQLite n'active pas les clés étrangères par défaut
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


def init_db() -> None:
    """Crée la base à partir de tables.sql + data.sql si elle n'existe pas encore.

    Le schéma vient du repo 4a-isi-projet-db : on n'utilise pas
    SQLModel.metadata.create_all() pour garder une seule source de vérité.
    """
    if DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        for name in ("tables.sql", "data.sql"):
            conn.executescript((SQL_DIR / name).read_text(encoding="utf-8"))
        conn.commit()
    except Exception:
        conn.close()
        DB_PATH.unlink(missing_ok=True)
        raise
    conn.close()


def get_session():
    """Dépendance FastAPI : une session par requête."""
    with Session(engine) as session:
        yield session
