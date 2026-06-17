from __future__ import annotations

from datetime import date

from sqlalchemy import func, select

from app.core.enums import MaintenanceStatus
from app.models.allocation import AssetAllocation
from app.models.asset import Asset
from app.models.department import Department
from app.models.employee import Employee
from app.models.maintenance import MaintenanceRecord
from app.models.transfer import AssetTransfer
from app.repositories.base import BaseRepository


class DashboardRepository(BaseRepository[Asset]):
    def count_assets(self, *, active_only: bool = False) -> int:
        stmt = select(func.count()).select_from(Asset)
        if active_only:
            stmt = stmt.where(Asset.is_active.is_(True))
        return self.db.execute(stmt).scalar_one()

    def count_employees(self, *, active_only: bool = False) -> int:
        stmt = select(func.count()).select_from(Employee)
        if active_only:
            stmt = stmt.where(Employee.is_active.is_(True))
        return self.db.execute(stmt).scalar_one()

    def count_departments(self, *, active_only: bool = False) -> int:
        stmt = select(func.count()).select_from(Department)
        if active_only:
            stmt = stmt.where(Department.is_active.is_(True))
        return self.db.execute(stmt).scalar_one()

    def assets_by_status(self) -> list[tuple[str, int]]:
        stmt = (
            select(Asset.current_status, func.count())
            .where(Asset.is_active.is_(True))
            .group_by(Asset.current_status)
            .order_by(Asset.current_status)
        )
        return [(status.value, count) for status, count in self.db.execute(stmt).all()]

    def assets_by_department(self) -> list[tuple[str, str, int]]:
        stmt = (
            select(Department.id, Department.name, func.count(Asset.id))
            .join(Asset, Asset.current_department_id == Department.id)
            .where(Asset.is_active.is_(True))
            .group_by(Department.id, Department.name)
            .order_by(func.count(Asset.id).desc(), Department.name)
        )
        rows = self.db.execute(stmt).all()
        return [(str(dep_id), dep_name, count) for dep_id, dep_name, count in rows]

    def maintenance_due_count(self) -> int:
        stmt = (
            select(func.count())
            .select_from(MaintenanceRecord)
            .where(
                MaintenanceRecord.status.in_(
                    [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]
                ),
                MaintenanceRecord.scheduled_date.is_not(None),
                MaintenanceRecord.scheduled_date <= date.today(),
            )
        )
        return self.db.execute(stmt).scalar_one()

    def recent_allocations(self, limit: int) -> list[AssetAllocation]:
        stmt = (
            select(AssetAllocation)
            .order_by(AssetAllocation.allocated_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def recent_transfers(self, limit: int) -> list[AssetTransfer]:
        stmt = (
            select(AssetTransfer)
            .order_by(AssetTransfer.transferred_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def recent_maintenance(self, limit: int) -> list[MaintenanceRecord]:
        stmt = (
            select(MaintenanceRecord)
            .order_by(MaintenanceRecord.updated_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
