"""add client request id to incident

Revision ID: 8a4f3c2d9b11
Revises: 7c2d4a9e6b1f
Create Date: 2026-06-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a4f3c2d9b11"
down_revision: Union[str, Sequence[str], None] = "7c2d4a9e6b1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "incident",
        sa.Column("client_request_id", sa.String(length=120), nullable=True),
    )
    op.create_index(
        op.f("ix_incident_client_request_id"),
        "incident",
        ["client_request_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_incident_client_request_id"), table_name="incident")
    op.drop_column("incident", "client_request_id")
