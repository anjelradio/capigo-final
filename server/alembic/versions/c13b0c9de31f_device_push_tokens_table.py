"""device push tokens table

Revision ID: c13b0c9de31f
Revises: a0e566a3824e
Create Date: 2026-04-26 20:12:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "c13b0c9de31f"
down_revision: Union[str, Sequence[str], None] = "a0e566a3824e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_push_token",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("state", sa.Boolean(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("modified_date", sa.DateTime(), nullable=False),
        sa.Column("deleted_date", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("device_id", sqlmodel.sql.sqltypes.AutoString(length=120), nullable=True),
        sa.Column("push_token", sqlmodel.sql.sqltypes.AutoString(length=400), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("push_token"),
    )
    op.create_index(op.f("ix_device_push_token_device_id"), "device_push_token", ["device_id"], unique=False)
    op.create_index(op.f("ix_device_push_token_push_token"), "device_push_token", ["push_token"], unique=False)
    op.create_index(op.f("ix_device_push_token_user_id"), "device_push_token", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_device_push_token_user_id"), table_name="device_push_token")
    op.drop_index(op.f("ix_device_push_token_push_token"), table_name="device_push_token")
    op.drop_index(op.f("ix_device_push_token_device_id"), table_name="device_push_token")
    op.drop_table("device_push_token")
