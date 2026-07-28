from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import tasks
from app.core.config import settings
from app.core.database import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "TaskHub API is running"}
