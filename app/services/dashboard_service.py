from __future__ import annotations

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    DepartmentAssetBreakdownItem,
    RecentActivityItem,
    StatusBreakdownItem,
)


class DashboardService:
    def __init__(self, repository: DashboardRepository) -> None:
        self.repository = repository

    def get_summary(self) -> DashboardSummaryResponse:
        total_assets = self.repository.count_assets(active_only=False)
        total_active_assets = self.repository.count_assets(active_only=True)
        total_employees = self.repository.count_employees(active_only=False)
        total_active_employees = self.repository.count_employees(active_only=True)
        total_departments = self.repository.count_departments(active_only=False)
        total_active_departments = self.repository.count_departments(active_only=True)

        assets_by_status = [
            StatusBreakdownItem(status=status, count=count)
            for status, count in self.repository.assets_by_status()
        ]

        assets_by_department = [
            DepartmentAssetBreakdownItem(
                department_id=department_id,
                department_name=department_name,
                count=count,
            )
            for department_id, department_name, count in self.repository.assets_by_department()
        ]

        maintenance_due_count = self.repository.maintenance_due_count()

        recent_activity = self._build_recent_activity(limit=5)

        return DashboardSummaryResponse(
            total_assets=total_assets,
            total_active_assets=total_active_assets,
            total_employees=total_employees,
            total_active_employees=total_active_employees,
            total_departments=total_departments,
            total_active_departments=total_active_departments,
            assets_by_status=assets_by_status,
            assets_by_department=assets_by_department,
            maintenance_due_count=maintenance_due_count,
            recent_activity=recent_activity,
        )

    def _build_recent_activity(self, *, limit: int) -> list[RecentActivityItem]:
        activity: list[RecentActivityItem] = []

        for row in self.repository.recent_allocations(limit=limit):
            action = row.action.value
            activity.append(
                RecentActivityItem(
                    activity_type=f"ALLOCATION_{action}",
                    occurred_at=row.allocated_at,
                    asset_id=str(row.asset_id),
                    message=f"Asset {action.lower()} for employee {row.employee_id}",
                )
            )

        for row in self.repository.recent_transfers(limit=limit):
            activity.append(
                RecentActivityItem(
                    activity_type="TRANSFER",
                    occurred_at=row.transferred_at,
                    asset_id=str(row.asset_id),
                    message=(
                        f"Asset transferred from department {row.from_department_id} "
                        f"to {row.to_department_id}"
                    ),
                )
            )

        for row in self.repository.recent_maintenance(limit=limit):
            activity.append(
                RecentActivityItem(
                    activity_type="MAINTENANCE",
                    occurred_at=row.updated_at,
                    asset_id=str(row.asset_id),
                    message=f"Maintenance status set to {row.status.value}",
                )
            )

        activity.sort(key=lambda item: item.occurred_at, reverse=True)
        return activity[:limit]
