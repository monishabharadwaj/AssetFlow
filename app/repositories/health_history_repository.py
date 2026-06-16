from __future__ import annotations

import uuid

from sqlalchemy import func, select

from app.models.health_history import AssetHealthHistory
from app.repositories.base import BaseRepository


class HealthHistoryRepository(BaseRepository[AssetHealthHistory]):
    def create(self, record: AssetHealthHistory) -> AssetHealthHistory:
        self.add(record)
        self.flush()
        return record

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[AssetHealthHistory], int]:
        stmt = select(AssetHealthHistory).where(AssetHealthHistory.asset_id == asset_id)
        count_stmt = (
            select(func.count())
            .select_from(AssetHealthHistory)
            .where(AssetHealthHistory.asset_id == asset_id)
        )

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = (
            stmt.order_by(AssetHealthHistory.recorded_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(self.db.execute(stmt).scalars().all())
        return items, total
