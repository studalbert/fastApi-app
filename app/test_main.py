import asyncio
from contextlib import asynccontextmanager

import pytest
from database import Base
from fastapi.testclient import TestClient
from main import app, get_session
from models import Recipe
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL_TEST = "sqlite+aiosqlite://"

# Создаём асинхронный движок
engine_test = create_async_engine(DATABASE_URL_TEST, echo=True)

# Создаём фабрику сессий
TestingSessionLocal = sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


# Переопределяем lifespan для тестов (убираем создание таблиц в основной БД)
@asynccontextmanager
async def any_test_lifespan(app):
    yield


app.router.lifespan_context = (
    any_test_lifespan  # Подменяем lifecycle на пустой
)


# Переопределяем get_session
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session  # Асинхронный генератор


# Фикстура для создания БД перед тестами
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Создаёт тестовую БД перед тестами и удаляет после."""

    async def init_db():
        async with engine_test.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)  # Создание таблиц

        async with TestingSessionLocal() as session:
            # Добавляем тестовые данные
            session.add_all(
                [
                    Recipe(
                        title="Пельмени",
                        cooking_time=20.0,
                        ingredients="Мука, вода, мясо",
                        description="Вкусные пельмени.",
                    ),
                    Recipe(
                        title="Борщ",
                        cooking_time=40.0,
                        ingredients="Свекла, капуста, картофель",
                        description="Классический борщ.",
                    ),
                ]
            )
            await session.commit()

    asyncio.run(init_db())  # Гарантируем, что БД создастся перед тестами

    yield  # Тесты выполняются здесь

    async def drop_db():
        async with engine_test.begin() as conn:
            await conn.run_sync(
                Base.metadata.drop_all
            )  # Удаление БД после тестов

    asyncio.run(drop_db())


# Фикстура для тестового клиента
@pytest.fixture(scope="function")
def client():
    """Создаёт тестовый клиент FastAPI с тестовой БД."""
    app.dependency_overrides[get_session] = (
        override_get_db  # Подмена зависимостей
    )
    with TestClient(app) as test_client:
        yield test_client  # Возвращаем синхронный клиент
    app.dependency_overrides.clear()  # Очищаем зависимости после тестов


def test_get_all_recipes(client):
    response = client.get("/recipes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_recipe(client):
    response = client.post(
        "/recipes",
        json={
            "title": "Пельмени",
            "cooking_time": 20.0,
            "ingredients": "Мука, вода, мясо",
            "description": "Вкусные пельмени.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Пельмени"
    assert data["cooking_time"] == 20.0


def test_create_recipe_with_error(client):
    response = client.post(
        "/recipes",
        json={
            "title": "Пельмени",
            "cooking_time": "string",
            "ingredients": "Мука, вода, мясо",
            "description": "Вкусные пельмени.",
        },
    )

    assert response.status_code == 422


def test_get_recipe_by_id(client):
    response = client.get("/recipes/2")
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert data["id"] == 2


def test_get_recipe_by_id_with_error(client):

    response = client.get("/recipes/str")
    assert response.status_code == 422

    response = client.get("/recipes/1000")
    assert response.status_code == 404
