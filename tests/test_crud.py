# import pytest
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.repositories.recipies import RecipeRepository
# from app.db.models import Recipe, Difficulty
# from app.api.schemas.recipe import RecipeCreate, RecipeUpdate
#
#
# @pytest.mark.asyncio
# async def test_create_recipe(db_session: AsyncSession):
#     repo = RecipeRepository(db_session)
#     recipe_in = RecipeCreate(
#         title="Test Recipe",
#         ingredients=["test", "ingredient"],
#         instructions="Just test it.",
#         cooking_time=10,
#         difficulty=Difficulty.easy,
#         cuisine="TestCuisine",
#         tags=["test", "quick"],
#     )
#
#     recipe = await repo.create(recipe_in.model_dump())
#     await db_session.commit()
#
#     assert recipe.id is not None
#     assert recipe.title == "Test Recipe"
#     assert "ingredient" in recipe.ingredients
#
#
# @pytest.mark.asyncio
# async def test_get_recipe(db_session: AsyncSession):
#     repo = RecipeRepository(db_session)
#     recipes = await repo.get_list()
#     recipe = await repo.get(recipes[0].id)
#
#     assert recipe is not None
#     assert isinstance(recipe, Recipe)
#
#
# @pytest.mark.asyncio
# async def test_update_recipe(db_session: AsyncSession):
#     repo = RecipeRepository(db_session)
#     recipes = await repo.get_list()
#     recipe_id = recipes[0].id
#
#     updated = await repo.update(recipe_id, {"title": "Updated Title"})
#     await db_session.commit()
#
#     assert updated.title == "Updated Title"
#
#
# @pytest.mark.asyncio
# async def test_delete_recipe(db_session: AsyncSession):
#     repo = RecipeRepository(db_session)
#     recipes = await repo.get_list()
#     recipe_id = recipes[0].id
#
#     await repo.delete(recipe_id)
#
#     deleted = await repo.get(recipe_id)
#     assert deleted is None
#
#
# @pytest.mark.asyncio
# async def test_list_recipes(db_session: AsyncSession):
#     repo = RecipeRepository(db_session)
#     recipes = await repo.get_list()
#
#     assert isinstance(recipes, list)
#     assert len(recipes) > 0
#     assert isinstance(recipes[0], Recipe)
