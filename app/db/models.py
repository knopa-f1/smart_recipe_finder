from sqlalchemy import Column, Integer, String, Text, Enum, ARRAY, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from app.api.schemas.enums import Difficulty
from app.api.schemas.recipe import RecipeOut
from app.db.database import Base


class Recipe(Base): # pylint: disable=too-few-public-methods
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    ingredients: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    cooking_time: Mapped[int] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty, name="difficulty_enum"), nullable=False)
    cuisine: Mapped[str] = mapped_column(String, nullable=True, index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    search_vector: Mapped[str] = mapped_column(TSVECTOR)
