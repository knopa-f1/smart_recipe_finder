import os
import uuid

import pytest
import pytest_asyncio

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from alembic import command
from alembic.config import Config


from app.api.schemas.enums import Difficulty
from app.core.config import settings
from app.db.models import Recipe
from app.services.recipe_service import RecipeService
from app.utils.unitofwork import UnitOfWork

TEST_DB_NAME = f"{settings.DB_NAME}_test_{uuid.uuid4().hex[:6]}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{TEST_DB_NAME}"
DATABASE_URL = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{TEST_DB_NAME}"
ADMIN_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/postgres"


@pytest.fixture(scope="session", autouse=True)
async def test_database():
    admin_engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.begin() as conn:
        conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

    engine = create_async_engine(ASYNC_DATABASE_URL, future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        recipes = [
            Recipe(
                title="Spaghetti Carbonara",
                ingredients=["spaghetti", "egg", "cheese", "bacon"],
                instructions="Boil pasta. Fry bacon. Mix with eggs and cheese.",
                cooking_time=20,
                difficulty=Difficulty.easy,
                cuisine="Italian",
                tags=["quick", "classic"],
            ),
            Recipe(
                title="Vegetarian Potato Cheese Bake",
                ingredients=["potato", "cheese", "onion"],
                instructions="Slice potatoes, add cheese, bake in oven.",
                cooking_time=40,
                difficulty=Difficulty.medium,
                cuisine="European",
                tags=["vegetarian"],
            ),
            Recipe(
                title="Egg and Flour Pancakes",
                ingredients=["egg", "flour", "milk"],
                instructions="Mix eggs, flour, milk. Fry in a pan.",
                cooking_time=15,
                difficulty=Difficulty.easy,
                cuisine="Universal",
                tags=["breakfast"],
            ),
            Recipe(
                title="Avocado Chicken Salad",
                ingredients=["avocado", "chicken", "lettuce", "tomato"],
                instructions="Mix avocado with cooked chicken and fresh vegetables.",
                cooking_time=25,
                difficulty=Difficulty.easy,
                cuisine="Healthy",
                tags=["lunch", "healthy"],
            ),
            Recipe(
                title="Tomato Pasta",
                ingredients=["pasta", "tomato", "garlic"],
                instructions="Boil pasta. Make tomato sauce with garlic. Mix together.",
                cooking_time=30,
                difficulty=Difficulty.easy,
                cuisine="Italian",
                tags=["beginner"],
            ),
        ]
        session.add_all(recipes)
        await session.commit()

    os.environ["DB_NAME"] = TEST_DB_NAME
    settings.DB_NAME = TEST_DB_NAME

    yield TEST_DB_NAME

    with admin_engine.begin() as conn:
        conn.execute(text(f'DROP DATABASE "{TEST_DB_NAME}" WITH (FORCE)'))

    admin_engine.dispose()
    await engine.dispose()


# @pytest.fixture(scope="session", autouse=True)
# def test_database():
#     # создаём отдельную БД для тестов
#     subprocess.run(
#         ["psql", ADMIN_URL, "-c", f'CREATE DATABASE "{TEST_DB_NAME}";'],
#         check=True,
#     )
#
#     os.environ["DB_NAME"] = TEST_DB_NAME
#     settings.DB_NAME = TEST_DB_NAME
#
#     subprocess.run(["alembic", "upgrade", "head"], check=True)
#
#     conn = psycopg2.connect(
#         dbname=TEST_DB_NAME,
#         user=settings.DB_USER,
#         password=settings.DB_PASS,
#         host=settings.DB_HOST,
#         port=settings.DB_PORT,
#     )
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO recipes (title, ingredients, instructions, cooking_time, difficulty, cuisine, tags)
#         VALUES
#         (
#             'Spaghetti Carbonara',
#             ARRAY['spaghetti','egg','cheese','bacon'],
#             'Boil pasta. Fry bacon. Mix with eggs and cheese.',
#             20, 'easy', 'Italian', ARRAY['quick','classic']
#         ),
#         (
#             'Vegetarian Potato Cheese Bake',
#             ARRAY['potato','cheese','onion'],
#             'Slice potatoes, add cheese, bake in oven.',
#             40, 'medium', 'European', ARRAY['vegetarian']
#         ),
#         (
#             'Egg and Flour Pancakes',
#             ARRAY['egg','flour','milk'],
#             'Mix eggs, flour, milk. Fry in a pan.',
#             15, 'easy', 'Universal', ARRAY['breakfast']
#         ),
#         (
#             'Avocado Chicken Salad',
#             ARRAY['avocado','chicken','lettuce','tomato'],
#             'Mix avocado with cooked chicken and fresh vegetables.',
#             25, 'easy', 'Healthy', ARRAY['lunch','healthy']
#         ),
#         (
#             'Tomato Pasta',
#             ARRAY['pasta','tomato','garlic'],
#             'Boil pasta. Make tomato sauce with garlic. Mix together.',
#             30, 'easy', 'Italian', ARRAY['beginner']
#         )
#     """)
#     conn.commit()
#     cur.close()
#     conn.close()
#
#     yield TEST_DB_NAME
#
#     subprocess.run(
#         ["psql", ADMIN_URL, "-c", f'DROP DATABASE "{TEST_DB_NAME}" WITH (FORCE);'],
#         check=True,
#     )


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(ASYNC_DATABASE_URL, future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def uow_factory(engine):
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return UnitOfWork(async_session_maker)


@pytest.fixture
def recipe_service(uow_factory):
    return RecipeService(uow_factory)
