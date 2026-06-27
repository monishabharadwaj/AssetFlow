import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.department import Department


class AssetTransfer(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "asset_transfers"

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    from_department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    to_department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    from_location: Mapped[str] = mapped_column(String(255), nullable=False)
    to_location: Mapped[str] = mapped_column(String(255), nullable=False)
    transferred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    reason: Mapped[str | None] = mapped_column(Text)
    performed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    asset: Mapped["Asset"] = relationship(
        back_populates="transfers",
        lazy="select",
    )
    from_department: Mapped["Department"] = relationship(
        foreign_keys=[from_department_id],
        lazy="select",
    )
    to_department: Mapped["Department"] = relationship(
        foreign_keys=[to_department_id],
        lazy="select",
    )
