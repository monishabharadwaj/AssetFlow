import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AllocationAction
from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.employee import Employee


class AssetAllocation(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "asset_allocations"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    action: Mapped[AllocationAction] = mapped_column(
        Enum(AllocationAction, name="allocation_action", native_enum=True),
        nullable=False,
    )
    allocated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    performed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    asset: Mapped["Asset"] = relationship(
        back_populates="allocations",
        lazy="select",
    )
    employee: Mapped["Employee"] = relationship(
        back_populates="allocations",
        lazy="select",
    )
