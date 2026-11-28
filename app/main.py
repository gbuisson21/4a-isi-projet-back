import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import FRONT_DIR
from app.routers import menu_controller, product_controller, planning_controller, user_controller
from app.routers.admin import admin_product_controller, admin_menu_controller, admin_planning_controller

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Pol-eat-heck API", lifespan=lifespan)

if os.environ['DEV']:
    print("Swagger enabled")
    app.swagger_ui_parameters = {"syntaxHighlight": True}
    app.docs_url = "/docs"
    app.openapi_url = "/openapi.json"

app.include_router(menu_controller.router)
app.include_router(product_controller.router)
app.include_router(planning_controller.router)
app.include_router(admin_product_controller.router)
app.include_router(admin_menu_controller.router)
app.include_router(user_controller.router)
app.include_router(admin_planning_controller.router)

# Front-end statique servi à la racine. Monté APRÈS les routers :
# les routes /api/... et /docs restent prioritaires.
if FRONT_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONT_DIR, html=True), name="front")
