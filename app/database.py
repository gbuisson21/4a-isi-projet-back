# app/database.py
import sqlite3

from sqlalchemy import event
from sqlmodel import Session, create_engine

from app.config import DB_PATH, SQL_DIR


def _enable_foreign_keys(dbapi_conn, _connection_record):
    # SQLite n'active pas les clés étrangères par défaut
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


class Database:
    def __init__(self):
        self.engine = create_engine(
            f"sqlite:///{DB_PATH}",
            connect_args={"check_same_thread": False},
        )
        event.listen(self.engine, "connect", _enable_foreign_keys)
        self._init_db()

    def _init_db(self):
        """Crée la base à partir de tables.sql + data.sql si elle n'existe pas."""
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

    def get_session(self):
        """Dépendance FastAPI : une session par requête."""
        with Session(self.engine) as session:
            yield session


# Instance unique, partagée par toute l'application
db = Database()