from __future__ import annotations

import uuid

from sqlalchemy import func, select

from app.models.allocation import AssetAllocation
from app.repositories.base import BaseRepository


class AllocationRepository(BaseRepository[AssetAllocation]):
    def create(self, allocation: AssetAllocation) -> AssetAllocation:
        self.add(allocation)
        self.flush()
        return allocation

    def get_open_allocation(self, asset_id: uuid.UUID) -> AssetAllocation | None:
        stmt = (
            select(AssetAllocation)
            .where(
                AssetAllocation.asset_id == asset_id,
                AssetAllocation.returned_at.is_(None),
            )
            .order_by(AssetAllocation.allocated_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[AssetAllocation], int]:
        stmt = select(AssetAllocation).where(AssetAllocation.asset_id == asset_id)
        count_stmt = (
            select(func.count())
            .select_from(AssetAllocation)
            .where(AssetAllocation.asset_id == asset_id)
        )

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = (
            stmt.order_by(AssetAllocation.allocated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def list_by_employee(
        self,
        employee_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[AssetAllocation], int]:
        stmt = select(AssetAllocation).where(AssetAllocation.employee_id == employee_id)
        count_stmt = (
            select(func.count())
            .select_from(AssetAllocation)
            .where(AssetAllocation.employee_id == employee_id)
        )

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = (
            stmt.order_by(AssetAllocation.allocated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(self.db.execute(stmt).scalars().all())
        return items, total
