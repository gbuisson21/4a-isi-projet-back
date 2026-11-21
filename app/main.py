from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Database
from app.routers import menu_controller, product_controller, planning_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Pol-eat-heck API", lifespan=lifespan)

app.include_router(menu_controller.router)
app.include_router(product_controller.router)
app.include_router(planning_controller.router)
