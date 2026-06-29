from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from app.core.access_scope import AccessContext
from app.core.enums import NotificationSeverity, NotificationType
from app.models.notification import Notification
from app.repositories.asset_repository import AssetRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.operations import NotificationListResponse, NotificationResponse


class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository,
        asset_repository: AssetRepository,
    ) -> None:
        self.repository = repository
        self.asset_repository = asset_repository

    @staticmethod
    def _department_id(scope: AccessContext | None) -> uuid.UUID | None:
        return scope.scoping_department_id() if scope else None

    def _assert_notification_access(
        self, notification: Notification, scope: AccessContext | None
    ) -> None:
        if scope is None or scope.is_org_wide:
            return
        if notification.asset_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )
        asset = self.asset_repository.get_by_id(notification.asset_id)
        if asset is None or asset.current_department_id != scope.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this notification",
            )

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

    def list_recent(
        self,
        *,
        limit: int = 20,
        unread_only: bool = False,
        scope: AccessContext | None = None,
    ) -> NotificationListResponse:
        department_id = self._department_id(scope)
        items = self.repository.list_recent(
            limit=limit,
            unread_only=unread_only,
            department_id=department_id,
        )
        return NotificationListResponse(
            items=[NotificationResponse.model_validate(item) for item in items],
            total=len(items),
            unread_count=self.repository.count_unread(department_id=department_id),
        )

    def mark_read(
        self, notification_id: uuid.UUID, scope: AccessContext | None = None
    ) -> NotificationResponse | None:
        record = self.repository.db.get(Notification, notification_id)
        if record is None:
            return None
        self._assert_notification_access(record, scope)
        record.is_read = True
        self.repository.commit()
        self.repository.refresh(record)
        return NotificationResponse.model_validate(record)

    def mark_all_read(self, scope: AccessContext | None = None) -> int:
        department_id = self._department_id(scope)
        if department_id is None:
            return self.repository.mark_all_read()
        items = self.repository.list_recent(
            limit=500,
            unread_only=True,
            department_id=department_id,
        )
        for item in items:
            item.is_read = True
        self.repository.commit()
        return len(items)
