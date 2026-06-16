import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import MaintenanceStatus, MaintenanceType
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.asset import Asset


class MaintenanceRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "maintenance_records"
    __table_args__ = (
        CheckConstraint(
            "cost IS NULL OR cost >= 0",
            name="chk_maintenance_records_cost",
        ),
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    maintenance_type: Mapped[MaintenanceType] = mapped_column(
        Enum(MaintenanceType, name="maintenance_type", native_enum=True),
        nullable=False,
    )
    status: Mapped[MaintenanceStatus] = mapped_column(
        Enum(MaintenanceStatus, name="maintenance_status", native_enum=True),
        default=MaintenanceStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    completed_date: Mapped[date | None] = mapped_column(Date)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_provider: Mapped[str | None] = mapped_column(String(200))
    performed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    asset: Mapped["Asset"] = relationship(
        back_populates="maintenance_records",
        lazy="joined",
    )
