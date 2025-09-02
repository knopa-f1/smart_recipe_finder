from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeOut
from app.core.logger import logger
from app.utils.nl_query_parser import parse_natural_query
from app.utils.openai_parser import OpenAIQueryParser
from app.utils.unitofwork import UnitOfWork


class RecipeService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.parser = OpenAIQueryParser()

    async def create_recipe(self, data: RecipeCreate) -> RecipeOut:
        logger.info("Creating recipe: %s", data.title)
        async with self.uow as uow:
            try:
                recipe = await uow.recipies.create(data.model_dump())
                await uow.commit()
                logger.info("Recipe created with id=%s", recipe.id)
                return RecipeOut.model_validate(recipe, from_attributes=True)
            except IntegrityError:
                await uow.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Recipe with this title and cuisine already exists",
                )

    async def get_recipe(self, recipe_id: int) -> RecipeOut | None:
        logger.info("Getting recipe with id=%s", recipe_id)
        async with self.uow as uow:
            recipe = await uow.recipies.get(recipe_id)
            if recipe:
                logger.info("Recipe found: id=%s title=%s", recipe.id, recipe.title)
                return RecipeOut.model_validate(recipe, from_attributes=True)
            logger.warning("Recipe with id=%s not found", recipe_id)
            return None

    async def list_recipes(self, skip: int = 0, limit: int = 20) -> list[RecipeOut]:
        logger.info("Listing recipes (skip=%s, limit=%s)", skip, limit)
        async with self.uow as uow:
            recipes = await uow.recipies.get_list(skip=skip, limit=limit)
            logger.info("Found %s recipes", len(recipes))
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]

    async def update_recipe(self, recipe_id: int, data: RecipeUpdate) -> RecipeOut | None:
        data_dict = data.model_dump(exclude_unset=True)
        logger.info("Updating recipe id=%s with data=%s", recipe_id, data_dict)
        async with self.uow as uow:
            recipe = await uow.recipies.update(recipe_id, data_dict)
            if recipe:
                await uow.commit()
                logger.info("Recipe id=%s updated successfully", recipe_id)
                return RecipeOut.model_validate(recipe, from_attributes=True)
            logger.warning("Failed to update recipe id=%s (not found)", recipe_id)
            return None

    async def delete_recipe(self, recipe_id: int) -> bool:
        logger.info("Deleting recipe id=%s", recipe_id)
        async with self.uow as uow:
            deleted = await uow.recipies.delete(recipe_id)
            if deleted:
                await uow.commit()
                logger.info("Recipe id=%s deleted successfully", recipe_id)
            else:
                logger.warning("Failed to delete recipe id=%s (not found)", recipe_id)
            return deleted

    async def filter_by_ingredients(
            self,
            include: list[str] | None = None,
            exclude: list[str] | None = None,
    ) -> list[RecipeOut]:
        logger.info("Filtering recipes include=%s exclude=%s", include, exclude)
        async with self.uow as uow:
            recipes = await uow.recipies.filter_by_ingredients(include, exclude)
            logger.info("Found %s recipes matching filter", len(recipes))
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]

    async def search(self, query: str) -> list[RecipeOut]:
        logger.info("Performing natural search with query='%s'", query)
        parsed_query = parse_natural_query(query)
        logger.info("Parsed query=%s", parsed_query)
        async with self.uow as uow:
            recipes = await uow.recipies.fulltext_search(parsed_query)
            logger.info("Fulltext search found %s recipes", len(recipes))
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]

    async def smart_search(self, query: str) -> list[RecipeOut]:
        logger.info("Performing smart search with OpenAI for query='%s'", query)
        parsed_query = await self.parser.parse(query)
        logger.info("Parsed query with OpenAI=%s", parsed_query)
        async with self.uow as uow:
            recipes = await uow.recipies.fulltext_search(parsed_query)
            logger.info("Smart search found %s recipes", len(recipes))
            return [RecipeOut.model_validate(r, from_attributes=True) for r in recipes]
