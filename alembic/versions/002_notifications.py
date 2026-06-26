"""Add notifications table for smart escalation engine

Revision ID: 002_notifications
Revises: 001_initial_schema
Create Date: 2026-06-26

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_notifications"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

notification_type_enum = postgresql.ENUM(
    "HIGH_RISK",
    "WARRANTY_EXPIRING",
    "HEALTH_DRIFT",
    "POLICY_AUTO_MAINTENANCE",
    "MAINTENANCE_DUE",
    name="notification_type",
    create_type=False,
)
notification_severity_enum = postgresql.ENUM(
    "LOW",
    "MEDIUM",
    "HIGH",
    name="notification_severity",
    create_type=False,
)


def upgrade() -> None:
    notification_type_enum.create(op.get_bind(), checkfirst=True)
    notification_severity_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "notification_type",
            notification_type_enum,
            nullable=False,
        ),
        sa.Column(
            "severity",
            notification_severity_enum,
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_notifications_notification_type", "notifications", ["notification_type"])
    op.create_index("ix_notifications_severity", "notifications", ["severity"])
    op.create_index("ix_notifications_asset_id", "notifications", ["asset_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])


def downgrade() -> None:
    op.drop_table("notifications")
    notification_severity_enum.drop(op.get_bind(), checkfirst=True)
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
