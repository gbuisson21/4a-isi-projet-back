from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import public


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Pol-eat-heck API", lifespan=lifespan)

app.include_router(public.router)
