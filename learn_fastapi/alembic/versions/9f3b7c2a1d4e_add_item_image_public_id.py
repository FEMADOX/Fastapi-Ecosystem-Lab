"""add_item_image_public_id

Revision ID: 9f3b7c2a1d4e
Revises: d8c2bf03d3ff
Create Date: 2026-06-12 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3b7c2a1d4e"
down_revision: Union[str, Sequence[str], None] = "d8c2bf03d3ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("image_public_id", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_column("image_public_id")
