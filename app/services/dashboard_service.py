from __future__ import annotations

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    AttentionItem,
    DashboardSummaryResponse,
    DepartmentAssetBreakdownItem,
    RecentActivityItem,
    StatusBreakdownItem,
)
from app.services import narrative as narr
from app.services.prediction_service import get_prediction_cache


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

        recent_activity = self._build_recent_activity(limit=15)
        attention_items = self._build_attention_items()

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
            attention_items=attention_items,
        )

    def _build_attention_items(self) -> list[AttentionItem]:
        items: list[AttentionItem] = []

        for prediction in get_prediction_cache().values():
            if prediction.risk_level.value != "HIGH":
                continue
            headline = f"AI high risk — {prediction.asset_tag}"
            message = narr.high_risk_attention_message(
                asset_name=prediction.asset_name or prediction.asset_tag or "Asset",
                score=prediction.health_score,
                risk_level=prediction.risk_level.value,
            )
            items.append(
                AttentionItem(
                    priority="HIGH",
                    item_type="HIGH_RISK",
                    asset_id=prediction.asset_id,
                    asset_tag=prediction.asset_tag or "",
                    asset_name=prediction.asset_name or "",
                    headline=headline,
                    message=message,
                    occurred_at=prediction.predicted_at,
                )
            )

        for record, asset in self.repository.maintenance_due_items(limit=8):
            headline = f"Maintenance overdue — {asset.asset_tag}"
            message = narr.maintenance_attention_message(
                asset_name=asset.name,
                scheduled_date=record.scheduled_date,
            )
            items.append(
                AttentionItem(
                    priority="HIGH",
                    item_type="MAINTENANCE_DUE",
                    asset_id=str(asset.id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    headline=headline,
                    message=message,
                    occurred_at=record.updated_at,
                )
            )

        for asset in self.repository.assets_in_maintenance(limit=6):
            headline = f"In maintenance — {asset.asset_tag}"
            message = narr.in_maintenance_attention_message(
                asset_name=asset.name,
                location=asset.current_location,
            )
            items.append(
                AttentionItem(
                    priority="MEDIUM",
                    item_type="IN_MAINTENANCE",
                    asset_id=str(asset.id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    headline=headline,
                    message=message,
                    occurred_at=asset.updated_at,
                )
            )

        for asset in self.repository.available_assignable_laptops(limit=4):
            headline = f"Ready to assign — {asset.asset_tag}"
            message = narr.available_attention_message(
                asset_name=asset.name,
                asset_tag=asset.asset_tag,
            )
            items.append(
                AttentionItem(
                    priority="LOW",
                    item_type="AVAILABLE_ASSIGNABLE",
                    asset_id=str(asset.id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    headline=headline,
                    message=message,
                    occurred_at=asset.updated_at,
                )
            )

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        items.sort(key=lambda i: priority_order.get(i.priority, 3))
        return items[:12]

    def _build_recent_activity(self, *, limit: int) -> list[RecentActivityItem]:
        activity: list[RecentActivityItem] = []

        for row in self.repository.recent_allocations(limit=limit):
            asset = row.asset
            employee = row.employee
            emp_name = narr.employee_display(employee.first_name, employee.last_name)
            headline = narr.allocation_headline(
                row.action,
                asset_name=asset.name,
                asset_tag=asset.asset_tag,
                employee_name=emp_name,
            )
            activity.append(
                RecentActivityItem(
                    activity_type=f"ALLOCATION_{row.action.value}",
                    occurred_at=row.allocated_at,
                    asset_id=str(row.asset_id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    headline=headline,
                    message=narr.allocation_message(
                        row.action,
                        asset_name=asset.name,
                        asset_tag=asset.asset_tag,
                        employee_name=emp_name,
                    ),
                )
            )

        for row in self.repository.recent_transfers(limit=limit):
            asset = row.asset
            from_name = row.from_department.name
            to_name = row.to_department.name
            headline = f"{asset.name} transferred to {to_name}"
            activity.append(
                RecentActivityItem(
                    activity_type="TRANSFER",
                    occurred_at=row.transferred_at,
                    asset_id=str(row.asset_id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    headline=headline,
                    message=narr.transfer_message(
                        asset_name=asset.name,
                        asset_tag=asset.asset_tag,
                        from_department=from_name,
                        to_department=to_name,
                        to_location=row.to_location,
                    ),
                )
            )

        for row in self.repository.recent_maintenance(limit=limit):
            asset = row.asset
            headline = f"{asset.name} maintenance {row.status.value.replace('_', ' ').lower()}"
            activity.append(
                RecentActivityItem(
                    activity_type="MAINTENANCE",
                    occurred_at=row.updated_at,
                    asset_id=str(row.asset_id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    headline=headline,
                    message=narr.maintenance_activity_message(
                        asset_name=asset.name,
                        asset_tag=asset.asset_tag,
                        status=row.status,
                        maintenance_type=row.maintenance_type.value,
                    ),
                )
            )

        activity.sort(key=lambda item: item.occurred_at, reverse=True)
        return activity[:limit]
