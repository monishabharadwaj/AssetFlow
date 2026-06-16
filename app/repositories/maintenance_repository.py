from __future__ import annotations

import uuid

from sqlalchemy import func, select

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
