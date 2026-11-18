import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Fichier SQLite utilisé par l'API (créé automatiquement au premier lancement)
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "kfet.db"))

# Dossier contenant tables.sql et data.sql (repo 4a-isi-projet-db)
SQL_DIR = Path(os.getenv("SQL_DIR", BASE_DIR.parent / "4a-isi-projet-db"))
