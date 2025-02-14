from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.app.database import engine
from backend.app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # позволяет FastAPI продолжить работу после старта

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "ChatGPT API is running!"}
