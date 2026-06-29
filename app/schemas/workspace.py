from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import UserRole


class MyAssetItem(BaseModel):
    id: UUID
    asset_tag: str
    name: str
    current_status: str
    asset_type_name: str | None = None


class MyMaintenanceItem(BaseModel):
    asset_id: UUID
    asset_tag: str
    maintenance_type: str
    scheduled_date: date | None
    status: str
    description: str | None = None


class MyNotificationItem(BaseModel):
    id: UUID
    title: str
    severity: str
    message: str
    asset_id: UUID | None
    created_at: datetime


class MyWorkspaceResponse(BaseModel):
    full_name: str
    department_name: str
    role: UserRole
    assigned_assets: list[MyAssetItem]
    upcoming_maintenance: list[MyMaintenanceItem]
    notifications: list[MyNotificationItem]
    department_asset_count: int
