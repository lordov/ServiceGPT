from fastapi.exceptions import RequestValidationError
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.core.exceptions.exceptions_handlers import validation_exception_handler


app = FastAPI()
app.include_router(auth_router)
app.include_router(chat_router)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 🔥 Разрешаем запросы с фронта
    allow_credentials=True,
    allow_methods=["*"],  # ✅ Разрешаем все методы (GET, POST, etc.)
    allow_headers=["*"],  # ✅ Разрешаем любые заголовки
)


@app.get("/")
async def root():
    return {"message": "ChatGPT API is running!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=5000, reload=True)
