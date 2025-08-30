from app.api.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from app.db.models import Recipe
from app.utils.unitofwork import UnitOfWork


class RecipeService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_recipe(self, data: RecipeCreate) -> RecipeOut:
        async with self.uow as uow:
            recipe = await uow.recipies.create(data)
            await uow.commit()
            return RecipeOut.model_validate(recipe)

    async def get_recipe(self, recipe_id: int) -> RecipeOut | None:
        async with self.uow as uow:
            recipe = await uow.recipies.get(recipe_id)
            if recipe:
                return RecipeOut.model_validate(recipe)
            return None

    async def list_recipes(self, skip: int = 0, limit: int = 20) -> list[RecipeOut]:
        async with self.uow as uow:
            recipes = await uow.recipies.list(skip=skip, limit=limit)
            return [RecipeOut.model_validate(r) for r in recipes]

    async def update_recipe(self, recipe_id: int, data: RecipeUpdate) -> RecipeOut | None:
        async with self.uow as uow:
            recipe = await uow.recipies.update(recipe_id, data)
            if recipe:
                await uow.commit()
                return RecipeOut.model_validate(recipe)
            return None

    async def delete_recipe(self, recipe_id: int) -> bool:
        async with self.uow as uow:
            deleted = await uow.recipies.delete(recipe_id)
            if deleted:
                await uow.commit()
            return deleted

    async def filter_by_ingredients(
        self,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> list[RecipeOut]:
        async with self.uow as uow:
            recipes = await uow.recipies.filter_by_ingredients(include, exclude)
            return [RecipeOut.model_validate(r) for r in recipes]

    async def search(self, query: str) -> list[RecipeOut]:
        async with self.uow as uow:
            recipes = await uow.recipies.fulltext_search(query)
            return [RecipeOut.model_validate(r) for r in recipes]
