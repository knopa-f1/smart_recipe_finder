from typing import List
from openai import AsyncOpenAI
from app.core.config import settings


class EmbeddingGenerator:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    async def generate(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding
