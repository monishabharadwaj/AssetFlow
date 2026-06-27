import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.asset import Asset


class AssetHealthHistory(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    """Time-series health snapshots for future FT-Transformer predictions."""

    __tablename__ = "asset_health_history"
    __table_args__ = (
        CheckConstraint(
            "health_score IS NULL OR (health_score >= 0 AND health_score <= 1)",
            name="chk_health_score",
        ),
        CheckConstraint(
            "condition_rating IS NULL OR (condition_rating >= 1 AND condition_rating <= 10)",
            name="chk_condition_rating",
        ),
        CheckConstraint(
            "depreciation_ratio IS NULL OR (depreciation_ratio >= 0 AND depreciation_ratio <= 1)",
            name="chk_depreciation_ratio",
        ),
        CheckConstraint("failure_count >= 0", name="chk_failure_count"),
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    health_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    condition_rating: Mapped[int | None] = mapped_column(SmallInteger)
    operational_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_since_last_maintenance: Mapped[int | None] = mapped_column(Integer)
    age_in_days: Mapped[int | None] = mapped_column(Integer)
    depreciation_ratio: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    raw_features: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    prediction_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)

    asset: Mapped["Asset"] = relationship(
        back_populates="health_history",
        lazy="select",
    )
