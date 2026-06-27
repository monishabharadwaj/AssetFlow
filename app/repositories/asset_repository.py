from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select

from app.core.enums import AssetStatus
from app.models.asset import Asset, AssetCategory, AssetType
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    def create(self, asset: Asset) -> Asset:
        self.add(asset)
        self.flush()
        return asset

    def get_by_id(self, asset_id: uuid.UUID) -> Asset | None:
        return self.db.get(Asset, asset_id)

    def get_by_tag(self, asset_tag: str) -> Asset | None:
        stmt = select(Asset).where(Asset.asset_tag == asset_tag)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_asset_type(self, asset_type_id: uuid.UUID) -> AssetType | None:
        return self.db.get(AssetType, asset_type_id)

    def list_categories(self) -> list[AssetCategory]:
        stmt = select(AssetCategory).order_by(AssetCategory.name)
        return list(self.db.execute(stmt).scalars().all())

    def list_asset_types(self, category_id: uuid.UUID | None = None) -> list[AssetType]:
        stmt = select(AssetType)
        if category_id is not None:
            stmt = stmt.where(AssetType.category_id == category_id)
        stmt = stmt.order_by(AssetType.name)
        return list(self.db.execute(stmt).scalars().all())

    def list(
        self,
        *,
        page: int,
        page_size: int,
        is_active: bool | None = None,
    ) -> tuple[list[Asset], int]:
        stmt = select(Asset)
        count_stmt = select(func.count()).select_from(Asset)

        if is_active is not None:
            stmt = stmt.where(Asset.is_active == is_active)
            count_stmt = count_stmt.where(Asset.is_active == is_active)

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Asset.name).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def search(
        self,
        *,
        page: int,
        page_size: int,
        name: str | None = None,
        asset_tag: str | None = None,
        serial_number: str | None = None,
        current_status: AssetStatus | None = None,
        current_department_id: uuid.UUID | None = None,
        current_location: str | None = None,
    ) -> tuple[list[Asset], int]:
        stmt = select(Asset).where(Asset.is_active.is_(True))
        count_stmt = select(func.count()).select_from(Asset).where(Asset.is_active.is_(True))

        if name:
            pattern = f"%{name}%"
            stmt = stmt.where(Asset.name.ilike(pattern))
            count_stmt = count_stmt.where(Asset.name.ilike(pattern))

        if asset_tag:
            pattern = f"%{asset_tag}%"
            stmt = stmt.where(Asset.asset_tag.ilike(pattern))
            count_stmt = count_stmt.where(Asset.asset_tag.ilike(pattern))

        if serial_number:
            pattern = f"%{serial_number}%"
            stmt = stmt.where(Asset.serial_number.ilike(pattern))
            count_stmt = count_stmt.where(Asset.serial_number.ilike(pattern))

        if current_status is not None:
            stmt = stmt.where(Asset.current_status == current_status)
            count_stmt = count_stmt.where(Asset.current_status == current_status)

        if current_department_id is not None:
            stmt = stmt.where(Asset.current_department_id == current_department_id)
            count_stmt = count_stmt.where(Asset.current_department_id == current_department_id)

        if current_location:
            pattern = f"%{current_location}%"
            stmt = stmt.where(Asset.current_location.ilike(pattern))
            count_stmt = count_stmt.where(Asset.current_location.ilike(pattern))

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Asset.name).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def update(self, asset: Asset, data: dict) -> Asset:
        return self.apply_partial_update(asset, data)

    def get_type_names_for_assets(
        self, asset_ids: list[uuid.UUID]
    ) -> dict[str, str]:
        if not asset_ids:
            return {}
        stmt = (
            select(Asset.id, AssetType.name)
            .join(AssetType, Asset.asset_type_id == AssetType.id)
            .where(Asset.id.in_(asset_ids))
        )
        return {str(asset_id): name for asset_id, name in self.db.execute(stmt).all()}
