from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StatusBreakdownItem(BaseModel):
    status: str
    count: int


class DepartmentAssetBreakdownItem(BaseModel):
    department_id: str
    department_name: str
    count: int


class RecentActivityItem(BaseModel):
    activity_type: str
    occurred_at: datetime
    asset_id: str
    asset_tag: str = ""
    asset_name: str = ""
    headline: str = ""
    message: str


class AttentionItem(BaseModel):
    priority: str
    item_type: str
    asset_id: str
    asset_tag: str
    asset_name: str = ""
    headline: str = ""
    message: str
    occurred_at: datetime | None = None


class DashboardSummaryResponse(BaseModel):
    total_assets: int
    total_active_assets: int
    total_employees: int
    total_active_employees: int
    total_departments: int
    total_active_departments: int
    assets_by_status: list[StatusBreakdownItem]
    assets_by_department: list[DepartmentAssetBreakdownItem]
    maintenance_due_count: int
    recent_activity: list[RecentActivityItem]
    attention_items: list[AttentionItem] = []
