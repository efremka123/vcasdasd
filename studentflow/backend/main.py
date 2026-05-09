import sys
from pathlib import Path

# Добавляем родительскую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models.database import init_db
from routers.transactions import router as transactions_router
from routers.finance import router as finance_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при запуске приложения"""
    # Инициализируем БД
    init_db()
    yield
    # Очистка при завершении (если нужно)


app = FastAPI(
    title="StudentFlow",
    description="Умный трекер личных финансов для студента",
    version="0.1.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(transactions_router)
app.include_router(finance_router)


@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "message": "Welcome to StudentFlow API 🎓",
        "docs": "/docs",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
