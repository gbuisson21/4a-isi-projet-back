from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import FRONT_DIR
from app.database import init_db
from app.routers import public

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Pol-eat-heck API", lifespan=lifespan)

app.include_router(public.router)

# Front-end statique servi à la racine. Monté APRÈS les routers :
# les routes /api/... et /docs restent prioritaires.
if FRONT_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONT_DIR, html=True), name="front")
