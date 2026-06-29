"""Link users to employees and remove duplicated profile fields.

Revision ID: 005_user_employee_link
Revises: 004_users
Create Date: 2026-06-27
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_user_employee_link"
down_revision: Union[str, None] = "004_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_employee_id_employees",
        "users",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_users_employee_id", "users", ["employee_id"], unique=True)

    # Legacy demo users are replaced by employee-linked accounts during seeding.
    op.execute(sa.text("DELETE FROM users"))

    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "email")
    op.drop_column("users", "full_name")

    op.alter_column("users", "employee_id", nullable=False)


def downgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("full_name", sa.String(length=150), nullable=True))

    op.drop_index("ix_users_employee_id", table_name="users")
    op.drop_constraint("fk_users_employee_id_employees", "users", type_="foreignkey")
    op.drop_column("users", "employee_id")

    op.create_index("ix_users_email", "users", ["email"], unique=True)
