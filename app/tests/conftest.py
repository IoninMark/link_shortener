import asyncio
import os
from typing import AsyncGenerator

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.crud import LinkCRUD
from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///./test.db"
)


@pytest.fixture(scope="session")
def event_loop():
    """Создание и закрытие цикла событий для тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Создание асинхронного движка базы данных для тестов."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        # Используем NullPool для тестов, чтобы избежать проблем с соединениями
        poolclass=NullPool
    )

    # Создание таблиц
    async with engine.begin() as conn:
        # Удаляем все таблицы перед созданием
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine

    # Очистка после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Создание и закрытие сессии базы данных для каждого теста."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    async_session = async_sessionmaker(
        connection,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await transaction.rollback()  # Откат изменений после каждого теста
        await connection.close()


@pytest.fixture
async def override_get_db(db_session: AsyncSession):
    """Патч функции get_db для использования тестовой базы данных."""

    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Создание и закрытие асинхронного HTTP клиента для тестов."""
    # `override_get_db` is a callable that yields the test `AsyncSession`.
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def crud(db_session: AsyncSession) -> LinkCRUD:
    """Патч CRUD-операций для использования тестовой базы данных."""
    return LinkCRUD(db_session)


@pytest.fixture
def sample_url() -> str:
    """Пример URL для тестов."""
    return "https://www.example.com/"
