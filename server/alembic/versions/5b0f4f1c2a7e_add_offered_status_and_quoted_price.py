"""add offered status and quoted price

Revision ID: 5b0f4f1c2a7e
Revises: 1f76da8c05c8
Create Date: 2026-06-01 14:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5b0f4f1c2a7e"
down_revision: Union[str, Sequence[str], None] = "1f76da8c05c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE assignmentstatus ADD VALUE IF NOT EXISTS 'OFFERED'")
    op.add_column(
        "request_assignment",
        sa.Column("quoted_price", sa.Numeric(10, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("request_assignment", "quoted_price")
