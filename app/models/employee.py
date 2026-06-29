import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.allocation import AssetAllocation
    from app.models.asset import Asset
    from app.models.department import Department
    from app.models.user import User


class Employee(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "employees"

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped["Department"] = relationship(
        back_populates="employees",
        lazy="select",
    )
    assigned_assets: Mapped[list["Asset"]] = relationship(
        back_populates="current_assigned_employee",
        lazy="select",
    )
    allocations: Mapped[list["AssetAllocation"]] = relationship(
        back_populates="employee",
        lazy="select",
    )
    user: Mapped["User | None"] = relationship(
        back_populates="employee",
        uselist=False,
        lazy="select",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
