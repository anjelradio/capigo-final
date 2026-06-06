"""add payments and final price

Revision ID: 7c2d4a9e6b1f
Revises: 5b0f4f1c2a7e
Create Date: 2026-06-05 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7c2d4a9e6b1f"
down_revision: Union[str, Sequence[str], None] = "5b0f4f1c2a7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE incidentstatus ADD VALUE IF NOT EXISTS 'PAYMENT_PENDING'")
    op.execute("ALTER TYPE assignmentstatus ADD VALUE IF NOT EXISTS 'PAYMENT_PENDING'")

    op.execute("ALTER TABLE request_assignment ADD COLUMN IF NOT EXISTS final_price NUMERIC(10, 2)")

    paymentprovider_create = postgresql.ENUM("STRIPE", name="paymentprovider")
    paymentstatus_create = postgresql.ENUM(
        "PENDING",
        "CHECKOUT_CREATED",
        "PAID",
        "FAILED",
        "CANCELLED",
        "EXPIRED",
        name="paymentstatus",
    )
    paymentprovider_create.create(op.get_bind(), checkfirst=True)
    paymentstatus_create.create(op.get_bind(), checkfirst=True)

    paymentprovider = postgresql.ENUM("STRIPE", name="paymentprovider", create_type=False)
    paymentstatus = postgresql.ENUM(
        "PENDING",
        "CHECKOUT_CREATED",
        "PAID",
        "FAILED",
        "CANCELLED",
        "EXPIRED",
        name="paymentstatus",
        create_type=False,
    )

    op.create_table(
        "payments",
        sa.Column("incident_id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("status", paymentstatus, nullable=False),
        sa.Column("provider", paymentprovider, nullable=False),
        sa.Column("stripe_checkout_session_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=255), nullable=True),
        sa.Column("checkout_url", sa.Text(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("state", sa.Boolean(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("modified_date", sa.DateTime(), nullable=False),
        sa.Column("deleted_date", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["assignment_id"], ["request_assignment.id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_assignment_id"), "payments", ["assignment_id"], unique=False)
    op.create_index(op.f("ix_payments_incident_id"), "payments", ["incident_id"], unique=False)
    op.create_index(op.f("ix_payments_provider"), "payments", ["provider"], unique=False)
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)
    op.create_index(
        op.f("ix_payments_stripe_checkout_session_id"),
        "payments",
        ["stripe_checkout_session_id"],
        unique=True,
    )
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_stripe_checkout_session_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_provider"), table_name="payments")
    op.drop_index(op.f("ix_payments_incident_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_assignment_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_column("request_assignment", "final_price")
    sa.Enum(name="paymentstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="paymentprovider").drop(op.get_bind(), checkfirst=True)
