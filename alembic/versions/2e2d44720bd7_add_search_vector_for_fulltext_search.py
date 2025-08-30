"""add search_vector for fulltext search

Revision ID: 2e2d44720bd7
Revises: fe0a6206765c
Create Date: 2025-08-30 17:17:36.067609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e2d44720bd7'
down_revision: Union[str, None] = 'fe0a6206765c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Функция обновления search_vector
    op.execute("""
    CREATE FUNCTION recipes_search_vector_update() RETURNS trigger AS $$
    BEGIN
      NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.ingredients, ' '), '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.instructions, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.cuisine, '')), 'C') ||
        setweight(to_tsvector('english', coalesce(NEW.difficulty::text, '')), 'C') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'C');
      RETURN NEW;
    END
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER trg_recipes_search_vector_update
    BEFORE INSERT OR UPDATE ON recipes
    FOR EACH ROW
    EXECUTE FUNCTION recipes_search_vector_update();
    """)

    op.execute("""
    CREATE INDEX idx_recipes_search_vector
    ON recipes USING gin (search_vector);
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_recipes_search_vector;")
    op.execute("DROP TRIGGER IF EXISTS trg_recipes_search_vector_update ON recipes;")
    op.execute("DROP FUNCTION IF EXISTS recipes_search_vector_update;")
