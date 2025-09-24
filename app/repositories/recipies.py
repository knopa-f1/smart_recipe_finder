from sqlalchemy import select, func

from app.db.models import Recipe
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

    async def fulltext_search(self, parsed_query: dict) -> list[Recipe]:
        query = select(Recipe)

        if parsed_query.get("fts"):
            query = query.where(
                Recipe.search_vector.op("@@")(func.plainto_tsquery("english", parsed_query["fts"]))
            )

        # cooking_time
        if parsed_query.get("cooking_time"):
            limit_lte = parsed_query["cooking_time"].get("lte")
            if limit_lte:
                query = query.where(Recipe.cooking_time <= limit_lte)

            limit_gte = parsed_query["cooking_time"].get("gte")
            if limit_gte:
                query = query.where(Recipe.cooking_time >= limit_gte)

        # difficulty
        if parsed_query.get("difficulty"):
            query = query.where(Recipe.difficulty == parsed_query["difficulty"])

        result = await self.session.execute(query)
        return result.scalars().all()

    async def vector_search(self, embedding: list[float], limit: int = 5, threshold: float = 0.3):
        stmt = (
            select(self.model)
            .where(Recipe.embedding.cosine_distance(embedding) < threshold)
            .order_by(self.model.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
