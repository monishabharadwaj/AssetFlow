from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select

from app.core.enums import MaintenanceStatus
from app.models.asset import Asset
from app.models.maintenance import MaintenanceRecord
from app.repositories.base import BaseRepository


class MaintenanceRepository(BaseRepository[MaintenanceRecord]):
    def create(self, record: MaintenanceRecord) -> MaintenanceRecord:
        self.add(record)
        self.flush()
        return record

    def get_by_id(self, record_id: uuid.UUID) -> MaintenanceRecord | None:
        return self.db.get(MaintenanceRecord, record_id)

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[MaintenanceRecord], int]:
        stmt = select(MaintenanceRecord).where(MaintenanceRecord.asset_id == asset_id)
        count_stmt = (
            select(func.count())
            .select_from(MaintenanceRecord)
            .where(MaintenanceRecord.asset_id == asset_id)
        )

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = (
            stmt.order_by(MaintenanceRecord.scheduled_date.desc().nullslast())
            .offset(offset)
            .limit(page_size)
        )
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def update(self, record: MaintenanceRecord, data: dict) -> MaintenanceRecord:
        return self.apply_partial_update(record, data)

    def list_due(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[tuple[MaintenanceRecord, Asset]], int]:
        today = date.today()
        base = (
            select(MaintenanceRecord, Asset)
            .join(Asset, Asset.id == MaintenanceRecord.asset_id)
            .where(
                MaintenanceRecord.status.in_(
                    [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]
                ),
                MaintenanceRecord.scheduled_date.is_not(None),
                MaintenanceRecord.scheduled_date <= today,
            )
        )
        count_stmt = (
            select(func.count())
            .select_from(MaintenanceRecord)
            .join(Asset, Asset.id == MaintenanceRecord.asset_id)
            .where(
                MaintenanceRecord.status.in_(
                    [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]
                ),
                MaintenanceRecord.scheduled_date.is_not(None),
                MaintenanceRecord.scheduled_date <= today,
            )
        )
        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = base.order_by(MaintenanceRecord.scheduled_date.asc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).all())
        return items, total
