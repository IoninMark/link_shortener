from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_db
from app.logger import app_logger
from app.routers import links


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Функция для управления жизненным циклом приложения FastAPI."""
    # Код, который выполняется при старте приложения (до обработки запросов).
    app_logger.info("Инициализация базы данных...")
    await init_db()  # Инициализируем базу данных при старте приложения.
    app_logger.info(
        "База данных инициализирована. Приложение готово к работе."
    )
    yield  # Здесь приложение будет работать и обрабатывать запросы.
    app_logger.info("Завершение работы приложения...")


app = FastAPI(
    title="Сервис сокращения ссылок",
    description="Простой сервис для создания коротких ссылок.",
    version="1.0.3",
    lifespan=lifespan
)
app.include_router(links.router)


@app.get("/")
def root():
    """Приветственный эндпоинт для проверки работоспособности приложения."""
    app_logger.debug("Получен запрос на корневой эндпоинт.")
    return {"message": "Приложение работает!",
            "version": app.version,
            "endpoints": [route.path for route in app.routes]}
