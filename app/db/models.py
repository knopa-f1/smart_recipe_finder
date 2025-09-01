from sqlalchemy import Integer, String, Text, Enum, ARRAY, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.api.schemas.enums import Difficulty
from app.db.database import Base


class Recipe(Base):  # pylint: disable=too-few-public-methods
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

    __table_args__ = (
        UniqueConstraint("title", "cuisine", name="uq_recipe_title_cuisine"),
    )
