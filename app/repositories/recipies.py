from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Recipe
from app.api.schemas.recipe import RecipeCreate, RecipeUpdate
from app.repositories.base import BaseRepository


class RecipeRepository(BaseRepository):
    model = Recipe

    async def filter_by_ingredients(
        self,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> list[Recipe]:
        query = select(Recipe)

        if include:
            for ingredient in include:
                query = query.where(func.array_position(Recipe.ingredients, ingredient) != None)
        if exclude:
            for ingredient in exclude:
                query = query.where(func.array_position(Recipe.ingredients, ingredient) == None)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def fulltext_search(self, query_str: str) -> list[Recipe]:
        query = select(Recipe).where(
            Recipe.search_vector.op("@@")(func.plainto_tsquery("english", query_str))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
