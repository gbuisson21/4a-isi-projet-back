from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import FRONT_DIR
from app.database import Database
from app.routers import menu_controller, product_controller, planning_controller, admin_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Pol-eat-heck API", lifespan=lifespan)

app.include_router(menu_controller.router)
app.include_router(product_controller.router)
app.include_router(planning_controller.router)
app.include_router(admin_controller.router)

# Front-end statique servi à la racine. Monté APRÈS les routers :
# les routes /api/... et /docs restent prioritaires.
if FRONT_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONT_DIR, html=True), name="front")
