from __future__ import annotations

import uuid

from sqlalchemy import func, select

from app.models.transfer import AssetTransfer
from app.repositories.base import BaseRepository


class TransferRepository(BaseRepository[AssetTransfer]):
    def create(self, transfer: AssetTransfer) -> AssetTransfer:
        self.add(transfer)
        self.flush()
        return transfer

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[AssetTransfer], int]:
        stmt = select(AssetTransfer).where(AssetTransfer.asset_id == asset_id)
        count_stmt = (
            select(func.count())
            .select_from(AssetTransfer)
            .where(AssetTransfer.asset_id == asset_id)
        )

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = (
            stmt.order_by(AssetTransfer.transferred_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(self.db.execute(stmt).scalars().all())
        return items, total
