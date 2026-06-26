"""Extend notification enums for positive operational events.

Revision ID: 003_notification_types
Revises: 002_notifications
Create Date: 2026-06-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "003_notification_types"
down_revision: Union[str, None] = "002_notifications"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_TYPES = (
    "HEALTH_IMPROVED",
    "MAINTENANCE_COMPLETED",
    "WARRANTY_RENEWED",
    "TRANSFER_COMPLETED",
    "INSPECTION_PASSED",
    "RISK_REDUCED",
)

_NEW_SEVERITIES = ("INFO", "SUCCESS")


def upgrade() -> None:
    for value in _NEW_TYPES:
        op.execute(f"ALTER TYPE notification_type ADD VALUE IF NOT EXISTS '{value}'")
    for value in _NEW_SEVERITIES:
        op.execute(f"ALTER TYPE notification_severity ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    pass
