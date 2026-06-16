"""Initial schema – core asset lifecycle tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-06-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

asset_status_enum = postgresql.ENUM(
    "AVAILABLE",
    "ASSIGNED",
    "IN_MAINTENANCE",
    "RETIRED",
    "DISPOSED",
    name="asset_status",
    create_type=False,
)
allocation_action_enum = postgresql.ENUM(
    "ASSIGN",
    "RETURN",
    "REASSIGN",
    name="allocation_action",
    create_type=False,
)
maintenance_type_enum = postgresql.ENUM(
    "PREVENTIVE",
    "CORRECTIVE",
    "INSPECTION",
    "UPGRADE",
    "OTHER",
    name="maintenance_type",
    create_type=False,
)
maintenance_status_enum = postgresql.ENUM(
    "SCHEDULED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
    name="maintenance_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    asset_status_enum.create(op.get_bind(), checkfirst=True)
    allocation_action_enum.create(op.get_bind(), checkfirst=True)
    maintenance_type_enum.create(op.get_bind(), checkfirst=True)
    maintenance_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "departments",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_departments_code"),
    )

    op.create_table(
        "asset_categories",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_asset_categories_name"),
    )

    op.create_table(
        "employees",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("department_id", sa.UUID(), nullable=False),
        sa.Column("employee_code", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("job_title", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_code", name="uq_employees_employee_code"),
        sa.UniqueConstraint("email", name="uq_employees_email"),
    )
    op.create_index("idx_employees_department_id", "employees", ["department_id"])

    op.create_table(
        "asset_types",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["asset_categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_id", "name", name="uq_asset_types_category_name"),
    )
    op.create_index("idx_asset_types_category_id", "asset_types", ["category_id"])

    op.create_table(
        "assets",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("asset_tag", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("asset_type_id", sa.UUID(), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("purchase_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "current_status",
            asset_status_enum,
            server_default="AVAILABLE",
            nullable=False,
        ),
        sa.Column("current_location", sa.String(length=255), server_default="Unassigned", nullable=False),
        sa.Column("current_department_id", sa.UUID(), nullable=False),
        sa.Column("current_assigned_employee_id", sa.UUID(), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("warranty_expiry", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("purchase_cost >= 0", name="chk_assets_purchase_cost"),
        sa.ForeignKeyConstraint(["asset_type_id"], ["asset_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["current_assigned_employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["current_department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_tag", name="uq_assets_asset_tag"),
    )
    op.create_index("idx_assets_asset_type_id", "assets", ["asset_type_id"])
    op.create_index("idx_assets_current_department_id", "assets", ["current_department_id"])
    op.create_index("idx_assets_current_assigned_employee_id", "assets", ["current_assigned_employee_id"])
    op.create_index("idx_assets_current_status", "assets", ["current_status"])
    op.create_index("idx_assets_current_location", "assets", ["current_location"])
    op.create_index("idx_assets_name", "assets", ["name"])

    op.create_table(
        "asset_allocations",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("action", allocation_action_enum, nullable=False),
        sa.Column("allocated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_asset_allocations_asset_id", "asset_allocations", ["asset_id"])
    op.create_index("idx_asset_allocations_employee_id", "asset_allocations", ["employee_id"])
    op.create_index("idx_asset_allocations_allocated_at", "asset_allocations", ["allocated_at"])

    op.create_table(
        "asset_transfers",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("from_department_id", sa.UUID(), nullable=False),
        sa.Column("to_department_id", sa.UUID(), nullable=False),
        sa.Column("from_location", sa.String(length=255), nullable=False),
        sa.Column("to_location", sa.String(length=255), nullable=False),
        sa.Column("transferred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["from_department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["to_department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_asset_transfers_asset_id", "asset_transfers", ["asset_id"])
    op.create_index("idx_asset_transfers_transferred_at", "asset_transfers", ["transferred_at"])

    op.create_table(
        "maintenance_records",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("maintenance_type", maintenance_type_enum, nullable=False),
        sa.Column(
            "status",
            maintenance_status_enum,
            server_default="SCHEDULED",
            nullable=False,
        ),
        sa.Column("scheduled_date", sa.Date(), nullable=True),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column("cost", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("service_provider", sa.String(length=200), nullable=True),
        sa.Column("performed_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("cost IS NULL OR cost >= 0", name="chk_maintenance_records_cost"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_maintenance_records_asset_id", "maintenance_records", ["asset_id"])
    op.create_index("idx_maintenance_records_status", "maintenance_records", ["status"])

    op.create_table(
        "asset_health_history",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("asset_id", sa.UUID(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("health_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("condition_rating", sa.SmallInteger(), nullable=True),
        sa.Column("operational_hours", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("failure_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("days_since_last_maintenance", sa.Integer(), nullable=True),
        sa.Column("age_in_days", sa.Integer(), nullable=True),
        sa.Column("depreciation_ratio", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("raw_features", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("prediction_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "health_score IS NULL OR (health_score >= 0 AND health_score <= 1)",
            name="chk_health_score",
        ),
        sa.CheckConstraint(
            "condition_rating IS NULL OR (condition_rating >= 1 AND condition_rating <= 10)",
            name="chk_condition_rating",
        ),
        sa.CheckConstraint(
            "depreciation_ratio IS NULL OR (depreciation_ratio >= 0 AND depreciation_ratio <= 1)",
            name="chk_depreciation_ratio",
        ),
        sa.CheckConstraint("failure_count >= 0", name="chk_failure_count"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_asset_health_history_asset_id", "asset_health_history", ["asset_id"])
    op.create_index("idx_asset_health_history_recorded_at", "asset_health_history", ["recorded_at"])

    op.execute(
        """
        INSERT INTO asset_categories (name, description) VALUES
            ('IT Equipment',      'Computers, servers, and networking devices'),
            ('Office Equipment',  'Desks, chairs, printers, and general office items'),
            ('Machinery',         'Industrial and production machinery'),
            ('Vehicles',          'Company-owned vehicles and transport assets')
        """
    )
    op.execute(
        """
        INSERT INTO asset_types (category_id, name, description)
        SELECT c.id, t.name, t.description
        FROM asset_categories c
        CROSS JOIN (VALUES
            ('IT Equipment',     'Laptop',             'Portable computing devices'),
            ('IT Equipment',     'Server',             'Physical and rack-mounted servers'),
            ('IT Equipment',     'Networking Device',  'Routers, switches, and access points'),
            ('Office Equipment', 'Printer',            'Office printing devices'),
            ('Office Equipment', 'Office Furniture',   'Desks, chairs, and cabinets'),
            ('Machinery',        'Production Machine', 'Manufacturing and production equipment'),
            ('Vehicles',         'Company Vehicle',    'Cars, vans, and fleet vehicles')
        ) AS t (category_name, name, description)
        WHERE c.name = t.category_name
        """
    )


def downgrade() -> None:
    op.drop_index("idx_asset_health_history_recorded_at", table_name="asset_health_history")
    op.drop_index("idx_asset_health_history_asset_id", table_name="asset_health_history")
    op.drop_table("asset_health_history")

    op.drop_index("idx_maintenance_records_status", table_name="maintenance_records")
    op.drop_index("idx_maintenance_records_asset_id", table_name="maintenance_records")
    op.drop_table("maintenance_records")

    op.drop_index("idx_asset_transfers_transferred_at", table_name="asset_transfers")
    op.drop_index("idx_asset_transfers_asset_id", table_name="asset_transfers")
    op.drop_table("asset_transfers")

    op.drop_index("idx_asset_allocations_allocated_at", table_name="asset_allocations")
    op.drop_index("idx_asset_allocations_employee_id", table_name="asset_allocations")
    op.drop_index("idx_asset_allocations_asset_id", table_name="asset_allocations")
    op.drop_table("asset_allocations")

    op.drop_index("idx_assets_name", table_name="assets")
    op.drop_index("idx_assets_current_location", table_name="assets")
    op.drop_index("idx_assets_current_status", table_name="assets")
    op.drop_index("idx_assets_current_assigned_employee_id", table_name="assets")
    op.drop_index("idx_assets_current_department_id", table_name="assets")
    op.drop_index("idx_assets_asset_type_id", table_name="assets")
    op.drop_table("assets")

    op.drop_index("idx_asset_types_category_id", table_name="asset_types")
    op.drop_table("asset_types")

    op.drop_index("idx_employees_department_id", table_name="employees")
    op.drop_table("employees")

    op.drop_table("asset_categories")
    op.drop_table("departments")

    maintenance_status_enum.drop(op.get_bind(), checkfirst=True)
    maintenance_type_enum.drop(op.get_bind(), checkfirst=True)
    allocation_action_enum.drop(op.get_bind(), checkfirst=True)
    asset_status_enum.drop(op.get_bind(), checkfirst=True)
