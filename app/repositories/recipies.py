from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Recipe
from app.api.schemas.recipe import RecipeCreate, RecipeUpdate


class RecipeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recipe_in: RecipeCreate) -> Recipe:
        recipe = Recipe(**recipe_in.model_dump())
        self.session.add(recipe)
        await self.session.flush()
        return recipe

    async def get(self, recipe_id: int) -> Recipe | None:
        result = await self.session.execute(
            select(Recipe).where(Recipe.id == recipe_id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 20) -> list[Recipe]:
        result = await self.session.execute(
            select(Recipe).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, recipe_id: int, recipe_in: RecipeUpdate) -> Recipe | None:
        values = recipe_in.model_dump(exclude_unset=True)
        if not values:
            return await self.get(recipe_id)

        await self.session.execute(
            update(Recipe)
            .where(Recipe.id == recipe_id)
            .values(**values)
        )
        await self.session.flush()
        return await self.get(recipe_id)

    async def delete(self, recipe_id: int) -> bool:
        result = await self.session.execute(
            delete(Recipe).where(Recipe.id == recipe_id)
        )
        return result.rowcount > 0

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
