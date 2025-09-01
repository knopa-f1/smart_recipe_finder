from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict):
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get(self, instance_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == instance_id)
        )
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 20) -> list:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, instance_id: int, data: dict):
        await self.session.execute(
            update(self.model)
            .where(self.model.id == instance_id)
            .values(**data)
        )
        await self.session.flush()
        return await self.get(instance_id)

    async def delete(self, instance_id: int) -> bool:
        instance = await self.get(instance_id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False
