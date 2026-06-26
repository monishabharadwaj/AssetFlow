from __future__ import annotations

import uuid

from app.core.enums import NotificationSeverity, NotificationType
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.schemas.operations import NotificationListResponse, NotificationResponse


class NotificationService:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    def create(
        self,
        *,
        notification_type: NotificationType,
        severity: NotificationSeverity,
        title: str,
        message: str,
        asset_id: uuid.UUID | None = None,
        commit: bool = True,
    ) -> NotificationResponse:
        record = Notification(
            notification_type=notification_type,
            severity=severity,
            title=title,
            message=message,
            asset_id=asset_id,
        )
        self.repository.create(record)
        if commit:
            self.repository.commit()
            self.repository.refresh(record)
        return NotificationResponse.model_validate(record)

    def create_many(self, items: list[dict]) -> int:
        for item in items:
            self.repository.create(
                Notification(
                    notification_type=item["notification_type"],
                    severity=item["severity"],
                    title=item["title"],
                    message=item["message"],
                    asset_id=item.get("asset_id"),
                )
            )
        if not items:
            return 0
        self.repository.commit()
        return len(items)

    def list_recent(self, *, limit: int = 20, unread_only: bool = False) -> NotificationListResponse:
        items = self.repository.list_recent(limit=limit, unread_only=unread_only)
        return NotificationListResponse(
            items=[NotificationResponse.model_validate(item) for item in items],
            total=len(items),
            unread_count=self.repository.count_unread(),
        )

    def mark_read(self, notification_id: uuid.UUID) -> NotificationResponse | None:
        record = self.repository.mark_read(notification_id)
        if record is None:
            return None
        self.repository.commit()
        return NotificationResponse.model_validate(record)

    def mark_all_read(self) -> int:
        count = self.repository.mark_all_read()
        self.repository.commit()
        return count
