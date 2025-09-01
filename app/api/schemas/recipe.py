from pydantic import BaseModel, Field, ConfigDict

from app.api.schemas.enums import Difficulty


class RecipeCreate(BaseModel):
    title: str = Field(..., max_length=255)
    ingredients: list[str]
    instructions: str
    cooking_time: int = Field(..., ge=0)
    difficulty: Difficulty
    cuisine: str | None = None
    tags: list[str] | None = []


class RecipeUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    ingredients: list[str] | None = None
    instructions: str | None = None
    cooking_time: int | None = Field(None, ge=0)
    difficulty: Difficulty | None = None
    cuisine: str | None = None
    tags: list[str] | None = None


class RecipeOut(RecipeCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
