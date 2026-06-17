from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.allocation import AssetAllocation
from app.models.health_history import AssetHealthHistory
from app.models.maintenance import MaintenanceRecord
from app.models.transfer import AssetTransfer
from app.repositories.base import BaseRepository


class TimelineRepository(BaseRepository[AssetAllocation]):
    def allocations_for_asset(self, asset_id: uuid.UUID) -> list[AssetAllocation]:
        stmt = (
            select(AssetAllocation)
            .where(AssetAllocation.asset_id == asset_id)
            .order_by(AssetAllocation.allocated_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def transfers_for_asset(self, asset_id: uuid.UUID) -> list[AssetTransfer]:
        stmt = (
            select(AssetTransfer)
            .where(AssetTransfer.asset_id == asset_id)
            .order_by(AssetTransfer.transferred_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def maintenance_for_asset(self, asset_id: uuid.UUID) -> list[MaintenanceRecord]:
        stmt = (
            select(MaintenanceRecord)
            .where(MaintenanceRecord.asset_id == asset_id)
            .order_by(MaintenanceRecord.updated_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def health_history_for_asset(self, asset_id: uuid.UUID) -> list[AssetHealthHistory]:
        stmt = (
            select(AssetHealthHistory)
            .where(AssetHealthHistory.asset_id == asset_id)
            .order_by(AssetHealthHistory.recorded_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())
