from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Database
from app.routers import public, menu_controller, product_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Pol-eat-heck API", lifespan=lifespan)

app.include_router(public.router)
app.include_router(menu_controller.router)
app.include_router(product_controller.router)
