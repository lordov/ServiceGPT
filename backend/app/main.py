import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.models.base import Base
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # позволяет FastAPI продолжить работу после старта

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "ChatGPT API is running!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=5000, reload=True)
