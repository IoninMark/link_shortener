import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()  # Загружаем переменные окружения из .env файла

DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///./links.db"
)
# 1. Создаем асинхронный движок (Async Engine)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

# 2. Создаем фабрику асинхронных сессий.
# expire_on_commit=False — важная настройка для async,
# чтобы объекты не "протухали" после комита.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


async def get_db():
    """Dependancy для получения асинхронной сессии базы данных."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Функция для инициализации базы данных (создания таблиц)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
