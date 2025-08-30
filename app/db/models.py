from sqlalchemy import Column, Integer, String, Text, Enum, ARRAY, Index
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import declarative_base
from app.api.schemas.enums import Difficulty
from app.db.database import Base


class Recipe(Base): # pylint: disable=too-few-public-methods
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    ingredients = Column(ARRAY(String), nullable=False)
    instructions = Column(Text, nullable=False)
    cooking_time = Column(Integer, nullable=True)
    difficulty = Column(Enum(Difficulty, name="difficulty_enum"), nullable=False)
    cuisine = Column(String(100), nullable=True, index=True)
    tags = Column(ARRAY(String), server_default="{}")

    search_vector = Column(TSVECTOR)
