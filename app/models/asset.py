import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AssetStatus
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.allocation import AssetAllocation
    from app.models.department import Department
    from app.models.employee import Employee
    from app.models.health_history import AssetHealthHistory
    from app.models.maintenance import MaintenanceRecord
    from app.models.transfer import AssetTransfer


class AssetCategory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "asset_categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    asset_types: Mapped[list["AssetType"]] = relationship(
        back_populates="category",
        lazy="select",
    )


class AssetType(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "asset_types"
    __table_args__ = (
        UniqueConstraint("category_id", "name", name="uq_asset_types_category_name"),
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    category: Mapped["AssetCategory"] = relationship(
        back_populates="asset_types",
        lazy="select",
    )
    assets: Mapped[list["Asset"]] = relationship(
        back_populates="asset_type",
        lazy="select",
    )


class Asset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint("purchase_cost >= 0", name="chk_assets_purchase_cost"),
    )

    asset_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    asset_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    purchase_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus, name="asset_status", native_enum=True),
        default=AssetStatus.AVAILABLE,
        nullable=False,
        index=True,
    )
    current_location: Mapped[str] = mapped_column(
        String(255),
        default="Unassigned",
        nullable=False,
        index=True,
    )
    current_department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    current_assigned_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        index=True,
    )
    serial_number: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    warranty_expiry: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    asset_type: Mapped["AssetType"] = relationship(
        back_populates="assets",
        lazy="select",
    )
    current_department: Mapped["Department"] = relationship(
        back_populates="assets",
        lazy="select",
    )
    current_assigned_employee: Mapped["Employee | None"] = relationship(
        back_populates="assigned_assets",
        lazy="select",
    )
    allocations: Mapped[list["AssetAllocation"]] = relationship(
        back_populates="asset",
        lazy="select",
        order_by="AssetAllocation.allocated_at",
    )
    transfers: Mapped[list["AssetTransfer"]] = relationship(
        back_populates="asset",
        lazy="select",
        order_by="AssetTransfer.transferred_at",
    )
    maintenance_records: Mapped[list["MaintenanceRecord"]] = relationship(
        back_populates="asset",
        lazy="select",
        order_by="MaintenanceRecord.scheduled_date",
    )
    health_history: Mapped[list["AssetHealthHistory"]] = relationship(
        back_populates="asset",
        lazy="select",
        order_by="AssetHealthHistory.recorded_at",
    )
