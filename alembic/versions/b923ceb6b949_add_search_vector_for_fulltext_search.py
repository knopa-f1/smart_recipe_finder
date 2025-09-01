"""add search_vector for fulltext search

Revision ID: b923ceb6b949
Revises: 9a4cec966178
Create Date: 2025-08-30 20:04:20.999973

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b923ceb6b949'
down_revision: Union[str, None] = '9a4cec966178'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE FUNCTION recipes_search_vector_update() RETURNS trigger AS $$
    BEGIN
      NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(array_to_string(NEW.ingredients, ' '), '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.instructions, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.cuisine, '')), 'B') ||
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
