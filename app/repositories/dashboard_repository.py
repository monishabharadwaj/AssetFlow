from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, load_only, noload

from app.core.enums import AssetStatus, MaintenanceStatus
from app.models.allocation import AssetAllocation
from app.models.asset import Asset
from app.models.department import Department
from app.models.employee import Employee
from app.models.maintenance import MaintenanceRecord
from app.models.transfer import AssetTransfer
from app.repositories.base import BaseRepository


def _asset_feed_options():
    return (
        noload(Asset.allocations),
        noload(Asset.transfers),
        noload(Asset.maintenance_records),
        noload(Asset.health_history),
        noload(Asset.asset_type),
        noload(Asset.current_department),
        noload(Asset.current_assigned_employee),
    )


def _department_feed_options():
    return (
        noload(Department.employees),
        noload(Department.assets),
    )


def _employee_feed_options():
    return (
        noload(Employee.assigned_assets),
        noload(Employee.allocations),
        noload(Employee.department),
    )


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
            .options(
                joinedload(AssetAllocation.asset)
                .load_only(Asset.id, Asset.asset_tag, Asset.name)
                .options(*_asset_feed_options()),
                joinedload(AssetAllocation.employee)
                .load_only(Employee.id, Employee.first_name, Employee.last_name)
                .options(*_employee_feed_options()),
            )
            .order_by(AssetAllocation.allocated_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def recent_transfers(self, limit: int) -> list[AssetTransfer]:
        stmt = (
            select(AssetTransfer)
            .options(
                joinedload(AssetTransfer.asset)
                .load_only(Asset.id, Asset.asset_tag, Asset.name)
                .options(*_asset_feed_options()),
                joinedload(AssetTransfer.to_department)
                .load_only(Department.id, Department.name)
                .options(*_department_feed_options()),
                joinedload(AssetTransfer.from_department)
                .load_only(Department.id, Department.name)
                .options(*_department_feed_options()),
            )
            .order_by(AssetTransfer.transferred_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def recent_maintenance(self, limit: int) -> list[MaintenanceRecord]:
        stmt = (
            select(MaintenanceRecord)
            .options(
                joinedload(MaintenanceRecord.asset)
                .load_only(Asset.id, Asset.asset_tag, Asset.name, Asset.updated_at)
                .options(*_asset_feed_options()),
            )
            .order_by(MaintenanceRecord.updated_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def maintenance_due_items(self, limit: int = 10) -> list[tuple[MaintenanceRecord, Asset]]:
        stmt = (
            select(MaintenanceRecord)
            .options(
                joinedload(MaintenanceRecord.asset)
                .load_only(Asset.id, Asset.asset_tag, Asset.name)
                .options(*_asset_feed_options()),
            )
            .where(
                MaintenanceRecord.status.in_(
                    [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]
                ),
                MaintenanceRecord.scheduled_date.is_not(None),
                MaintenanceRecord.scheduled_date <= date.today(),
            )
            .order_by(MaintenanceRecord.scheduled_date.asc())
            .limit(limit)
        )
        records = self.db.execute(stmt).scalars().all()
        return [(r, r.asset) for r in records]

    def recent_completed_maintenance(
        self, limit: int = 5
    ) -> list[tuple[MaintenanceRecord, Asset]]:
        stmt = (
            select(MaintenanceRecord, Asset)
            .join(Asset, Asset.id == MaintenanceRecord.asset_id)
            .where(
                MaintenanceRecord.status == MaintenanceStatus.COMPLETED,
                MaintenanceRecord.completed_date.is_not(None),
            )
            .order_by(MaintenanceRecord.completed_date.desc())
            .limit(limit)
        )
        return [(record, asset) for record, asset in self.db.execute(stmt).all()]

    def assets_in_maintenance(self, limit: int = 10) -> list[Asset]:
        stmt = (
            select(Asset)
            .options(*_asset_feed_options())
            .where(
                Asset.is_active.is_(True),
                Asset.current_status == AssetStatus.IN_MAINTENANCE,
            )
            .order_by(Asset.updated_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def assets_by_type(self) -> list[tuple[str, int]]:
        from app.models.asset import AssetType

        stmt = (
            select(AssetType.name, func.count(Asset.id))
            .join(Asset, Asset.asset_type_id == AssetType.id)
            .where(Asset.is_active.is_(True))
            .group_by(AssetType.name)
            .order_by(func.count(Asset.id).desc(), AssetType.name)
        )
        return [(name, count) for name, count in self.db.execute(stmt).all()]

    def count_assets_by_type_name(self, type_name: str) -> int:
        from app.models.asset import AssetType

        stmt = (
            select(func.count())
            .select_from(Asset)
            .join(AssetType, Asset.asset_type_id == AssetType.id)
            .where(Asset.is_active.is_(True), AssetType.name.ilike(type_name))
        )
        return self.db.execute(stmt).scalar_one()

    def warranty_expiring_soon(self, *, within_days: int = 30, limit: int = 10) -> list[Asset]:
        from datetime import timedelta

        cutoff = date.today() + timedelta(days=within_days)
        stmt = (
            select(Asset)
            .where(
                Asset.is_active.is_(True),
                Asset.warranty_expiry.is_not(None),
                Asset.warranty_expiry <= cutoff,
                Asset.warranty_expiry >= date.today(),
            )
            .order_by(Asset.warranty_expiry.asc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def available_assignable_laptops(self, limit: int = 5) -> list[Asset]:
        from app.models.asset import AssetType

        stmt = (
            select(Asset)
            .join(AssetType, Asset.asset_type_id == AssetType.id)
            .options(*_asset_feed_options())
            .where(
                Asset.is_active.is_(True),
                Asset.current_status == AssetStatus.AVAILABLE,
                AssetType.name.in_(["Laptop", "Desktop Workstation"]),
            )
            .order_by(Asset.updated_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
