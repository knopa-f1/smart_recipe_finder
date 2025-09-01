from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from app.utils.nl_query_parser import parse_natural_query
from app.utils.openai_parser import OpenAIQueryParser
from app.utils.unitofwork import UnitOfWork


class RecipeService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.parser = OpenAIQueryParser()

    async def create_recipe(self, data: RecipeCreate) -> RecipeOut:
        async with self.uow as uow:
            try:
                recipe = await uow.recipies.create(data.model_dump())
                await uow.commit()
                return RecipeOut.model_validate(recipe, from_attributes=True)
            except IntegrityError:
                await uow.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Recipe with this title and cuisine already exists",
                )

    async def get_recipe(self, recipe_id: int) -> RecipeOut | None:
        async with self.uow as uow:
            recipe = await uow.recipies.get(recipe_id)
            if recipe:
                return RecipeOut.model_validate(recipe, from_attributes=True)
            return None

    async def list_recipes(self, skip: int = 0, limit: int = 20) -> list[RecipeOut]:
        async with self.uow as uow:
            recipes = await uow.recipies.get_list(skip=skip, limit=limit)
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]

    async def update_recipe(self, recipe_id: int, data: RecipeUpdate) -> RecipeOut | None:
        async with self.uow as uow:
            recipe = await uow.recipies.update(recipe_id, data.model_dump(exclude_unset=True))
            if recipe:
                await uow.commit()
                return RecipeOut.model_validate(recipe, from_attributes=True)
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
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]

    async def search(self, query: str) -> list[RecipeOut]:
        parsed_query = parse_natural_query(query)
        async with self.uow as uow:
            recipes = await uow.recipies.fulltext_search(parsed_query)
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]

    async def smart_search(self, query: str) -> list[RecipeOut]:
        parsed_query = await self.parser.parse(query)
        async with self.uow as uow:
            recipes = await uow.recipies.fulltext_search(parsed_query)
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]
