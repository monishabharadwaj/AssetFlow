from __future__ import annotations

import uuid

from sqlalchemy import func, select

from app.models.notification import Notification
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def create(self, notification: Notification) -> Notification:
        self.add(notification)
        self.flush()
        return notification

    def list_recent(
        self,
        *,
        limit: int = 20,
        unread_only: bool = False,
    ) -> list[Notification]:
        stmt = select(Notification)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_unread(self) -> int:
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.is_read.is_(False))
        )
        return self.db.execute(stmt).scalar_one()

    def mark_read(self, notification_id: uuid.UUID) -> Notification | None:
        notification = self.db.get(Notification, notification_id)
        if notification is None:
            return None
        notification.is_read = True
        self.flush()
        return notification

    def list_for_assets(
        self,
        asset_ids: list[uuid.UUID],
        *,
        limit: int = 10,
    ) -> list[Notification]:
        if not asset_ids:
            return []
        stmt = (
            select(Notification)
            .where(Notification.asset_id.in_(asset_ids))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def mark_all_read(self) -> int:
        stmt = select(Notification).where(Notification.is_read.is_(False))
        items = list(self.db.execute(stmt).scalars().all())
        for item in items:
            item.is_read = True
        self.flush()
        return len(items)
