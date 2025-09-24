"""add embedding vector to recipes

Revision ID: f18aab544368
Revises: 85c833f120b9
Create Date: 2025-09-24 11:45:51.412046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'f18aab544368'
down_revision: Union[str, None] = '85c833f120b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column("embedding", Vector(dim=1536))
    )


def downgrade() -> None:
    op.drop_column("recipes", "embedding")
