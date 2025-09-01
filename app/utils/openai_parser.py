import json
from openai import AsyncOpenAI
from app.core.config import settings


class OpenAIQueryParser:
    def __init__(self, api_key: str | None = None, model: str = "gpt-5"):
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.model = model

    @staticmethod
    def _build_prompt(query: str) -> str:
        return f"""
        You are a query parser for a recipe database.

        Database fields:
        - title (string)
        - ingredients (array of strings)
        - instructions (text)
        - cuisine (string)
        - difficulty (enum: easy, medium, hard)
        - tags (array of strings)
        - cooking_time (int, minutes)

        There is also a special full-text search column called `search_vector`.
        It is generated from:
        - title (weight A)
        - ingredients (weight A)
        - instructions (weight B)
        - cuisine (weight B)
        - difficulty (weight C)
        - tags (weight C)

        Your task:
        1. Extract numeric/time constraints (e.g. "under 30 minutes") → `cooking_time`.
        2. Extract difficulty levels ("easy", "medium", "hard") → `difficulty`.
        3. For everything else (keywords that might appear in title, ingredients, 
           instructions, cuisine, or tags), collect them into `"fts"`. 
           This `"fts"` string will be used against the `search_vector`.

        User query: "{query}"

        Return **only valid JSON** with this structure:
        {{
            "fts": "<fts string for postgres full-text search>",
            "cooking_time": {{"lte": <int>}} OR null,
            "difficulty": "<easy|medium|hard>" OR null
        }}
        """

    async def parse(self, query: str) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful query-to-SQL parser."},
                {"role": "user", "content": self._build_prompt(query)},
            ],
            temperature=1,
        )

        raw = response.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"fts": query, "cooking_time": None, "difficulty": None}
