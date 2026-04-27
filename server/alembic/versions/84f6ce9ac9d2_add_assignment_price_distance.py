"""add assignment price distance

Revision ID: 84f6ce9ac9d2
Revises: 1985c7bdaeee
Create Date: 2026-04-25 22:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "84f6ce9ac9d2"
down_revision: Union[str, Sequence[str], None] = "1985c7bdaeee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "request_assignment",
        sa.Column("distance_km", sa.Numeric(precision=10, scale=3), nullable=True),
    )
    op.add_column(
        "request_assignment",
        sa.Column("delivery_price", sa.Numeric(precision=10, scale=2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("request_assignment", "delivery_price")
    op.drop_column("request_assignment", "distance_km")
