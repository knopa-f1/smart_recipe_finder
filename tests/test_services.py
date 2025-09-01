import pytest
from app.services.recipe_service import RecipeService
from app.api.schemas.recipe import RecipeCreate, RecipeUpdate
from app.api.schemas.enums import Difficulty
from app.utils.openai_parser import OpenAIQueryParser

@pytest.mark.asyncio
async def test_create_recipe(recipe_service: RecipeService):
    recipe_in = RecipeCreate(
        title="Service Test Recipe",
        ingredients=["x", "y"],
        instructions="mix x and y",
        cooking_time=5,
        difficulty=Difficulty.easy,
        cuisine="TestCuisine",
        tags=["quick"],
    )

    recipe = await recipe_service.create_recipe(recipe_in)

    assert recipe.id is not None
    assert recipe.title == "Service Test Recipe"


@pytest.mark.asyncio
async def test_get_recipe(recipe_service: RecipeService):
    recipes = await recipe_service.list_recipes()
    recipe = await recipe_service.get_recipe(recipes[0].id)

    assert recipe is not None
    assert recipe.id == recipes[0].id


@pytest.mark.asyncio
async def test_update_recipe(recipe_service: RecipeService):
    recipe_in = RecipeCreate(
        title="Service Test To Update Recipe",
        ingredients=["x", "y"],
        instructions="mix x and y",
        cooking_time=5,
        difficulty=Difficulty.easy,
        cuisine="TestToUpdateCuisine",
        tags=["quick"],
    )

    recipe = await recipe_service.create_recipe(recipe_in)
    recipe_id = recipe.id

    updated = await recipe_service.update_recipe(recipe_id, RecipeUpdate(title="Updated Service Title", cooking_time=20))
    assert updated.title == "Updated Service Title"


@pytest.mark.asyncio
async def test_delete_recipe(recipe_service: RecipeService):
    recipe_in = RecipeCreate(
        title="Service Test To Delete Recipe",
        ingredients=["x", "y"],
        instructions="mix x and y",
        cooking_time=5,
        difficulty=Difficulty.easy,
        cuisine="TestToDeleteCuisine",
        tags=["quick"],
    )

    recipe = await recipe_service.create_recipe(recipe_in)
    recipe_id = recipe.id

    await recipe_service.delete_recipe(recipe_id)
    deleted = await recipe_service.get_recipe(recipe_id)

    assert deleted is None


@pytest.mark.asyncio
async def test_search_basic(recipe_service: RecipeService):
    results = await recipe_service.search("Italian")
    assert any(r.cuisine == "Italian" for r in results)


@pytest.mark.asyncio
async def test_filter_by_ingredients(recipe_service: RecipeService):
    results = await recipe_service.filter_by_ingredients(["egg", "flour"])
    assert any("egg" in r.ingredients and "flour" in r.ingredients for r in results)

@pytest.mark.asyncio
@pytest.mark.parametrize("query,expected", [
    ("Quick Italian recipes under 30 minutes", "Spaghetti Carbonara"),
    ("Vegetarian recipes using potatoes and cheese", "Vegetarian Potato Cheese Bake"),
    ("What can I cook with eggs and flour?", "Egg and Flour Pancakes"),
    ("Healthy lunches with avocado", "Avocado Chicken Salad"),
    ("Recipes for beginner cooks", "Tomato Pasta"),
])
async def test_smart_search(monkeypatch, recipe_service: RecipeService, query, expected):
    async def fake_parse(self, query: str):
        mapping = {
            "Quick Italian recipes under 30 minutes": {"fts": "italian", "cooking_time": {"lte": 30}, "difficulty": None},
            "Vegetarian recipes using potatoes and cheese": {"fts": "vegetarian", "cooking_time": None, "difficulty": None},
            "What can I cook with eggs and flour?": {"fts": "egg flour", "cooking_time": None, "difficulty": None},
            "Healthy lunches with avocado": {"fts": "avocado", "cooking_time": None, "difficulty": None},
            "Recipes for beginner cooks": {"fts": "beginner", "cooking_time": None, "difficulty": Difficulty.easy},
        }
        return mapping[query]

    monkeypatch.setattr(OpenAIQueryParser, "parse", fake_parse)

    results = await recipe_service.smart_search(query)
    titles = [r.title for r in results]
    assert expected in titles
