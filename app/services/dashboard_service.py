from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone

from app.core.access_scope import AccessContext
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    AttentionItem,
    DashboardSummaryResponse,
    DepartmentAssetBreakdownItem,
    RecentActivityItem,
    StatusBreakdownItem,
)
from app.services import narrative as narr
from app.services.prediction_service import PredictionService


class DashboardService:
    def __init__(
        self,
        repository: DashboardRepository,
        prediction_service: PredictionService,
    ) -> None:
        self.repository = repository
        self.prediction_service = prediction_service

    def get_summary(self, scope: AccessContext | None = None) -> DashboardSummaryResponse:
        department_id = scope.scoping_department_id() if scope else None

        total_assets = self.repository.count_assets(active_only=False, department_id=department_id)
        total_active_assets = self.repository.count_assets(active_only=True, department_id=department_id)
        total_employees = self.repository.count_employees(active_only=False, department_id=department_id)
        total_active_employees = self.repository.count_employees(active_only=True, department_id=department_id)
        total_departments = (
            1
            if department_id is not None
            else self.repository.count_departments(active_only=False)
        )
        total_active_departments = (
            1
            if department_id is not None
            else self.repository.count_departments(active_only=True)
        )

        assets_by_status = [
            StatusBreakdownItem(status=status, count=count)
            for status, count in self.repository.assets_by_status(department_id=department_id)
        ]

        assets_by_department = [
            DepartmentAssetBreakdownItem(
                department_id=department_id,
                department_name=department_name,
                count=count,
            )
            for department_id, department_name, count in self.repository.assets_by_department(
                department_id=department_id
            )
        ]

        maintenance_due_count = self.repository.maintenance_due_count(department_id=department_id)

        recent_activity = self._build_recent_activity(limit=15, department_id=department_id)
        attention_items = self._build_attention_items(department_id=department_id)

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

    def _build_attention_items(self, department_id: uuid.UUID | None = None) -> list[AttentionItem]:
        items: list[AttentionItem] = []

        for prediction in self.prediction_service.get_all_cached_high_risk():
            if department_id is not None and str(getattr(prediction, "department_id", "")) != str(department_id):
                continue
            headline = f"AI high risk — {prediction.asset_tag}"
            message = narr.high_risk_attention_message(
                asset_tag=prediction.asset_tag or "",
                asset_type=prediction.asset_type_name,
                department_name=prediction.department_name,
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
            if department_id is not None and asset.current_department_id != department_id:
                continue
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
            if department_id is not None and asset.current_department_id != department_id:
                continue
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
            if department_id is not None and asset.current_department_id != department_id:
                continue
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

    def _build_recent_activity(
        self, *, limit: int, department_id: uuid.UUID | None = None
    ) -> list[RecentActivityItem]:
        activity: list[RecentActivityItem] = []

        for row in self.repository.recent_allocations(limit=limit):
            asset = row.asset
            if department_id is not None and asset.current_department_id != department_id:
                continue
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
            if department_id is not None and asset.current_department_id != department_id:
                continue
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
            if department_id is not None and asset.current_department_id != department_id:
                continue
            status = row.status.value
            event_date = row.completed_date or row.scheduled_date
            occurred = (
                datetime.combine(event_date, time(12, 0), tzinfo=timezone.utc)
                if event_date
                else row.updated_at
            )
            if status == "COMPLETED":
                activity_type = "MAINTENANCE_COMPLETED"
                headline = f"{asset.name} maintenance completed"
            elif status in ("SCHEDULED", "IN_PROGRESS"):
                activity_type = "MAINTENANCE_SCHEDULED"
                headline = f"{asset.name} maintenance scheduled"
            else:
                activity_type = "MAINTENANCE"
                headline = f"{asset.name} maintenance {status.replace('_', ' ').lower()}"
            activity.append(
                RecentActivityItem(
                    activity_type=activity_type,
                    occurred_at=occurred,
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

        for asset in self.repository.recently_registered_assets(limit=limit):
            occurred = datetime.combine(asset.purchase_date, time(9, 0), tzinfo=timezone.utc)
            type_name = asset.asset_type.name if asset.asset_type else "asset"
            activity.append(
                RecentActivityItem(
                    activity_type="REGISTRATION",
                    occurred_at=occurred,
                    asset_id=str(asset.id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    headline=f"{asset.name} added to inventory",
                    message=(
                        f"{asset.name} ({asset.asset_tag}) — a {type_name.lower()} — "
                        "was registered in AssetFlow."
                    ),
                )
            )

        return self._balance_activity(activity, limit=limit)

    @staticmethod
    def _activity_family(activity_type: str) -> str:
        if activity_type.startswith("ALLOCATION"):
            return "ALLOCATION"
        if activity_type.startswith("MAINTENANCE"):
            return "MAINTENANCE"
        return activity_type

    def _balance_activity(
        self, activity: list[RecentActivityItem], *, limit: int
    ) -> list[RecentActivityItem]:
        """Round-robin across event families so the feed stays varied rather than
        being dominated by whichever event type was most recently timestamped."""
        families: dict[str, list[RecentActivityItem]] = {}
        for item in activity:
            families.setdefault(self._activity_family(item.activity_type), []).append(item)
        for bucket in families.values():
            bucket.sort(key=lambda i: i.occurred_at, reverse=True)

        order = sorted(
            families.keys(),
            key=lambda f: families[f][0].occurred_at,
            reverse=True,
        )
        selected: list[RecentActivityItem] = []
        idx = 0
        while len(selected) < limit and any(families.values()):
            family = order[idx % len(order)]
            bucket = families[family]
            if bucket:
                selected.append(bucket.pop(0))
            idx += 1
            if idx > limit * len(order) * 2:
                break
        selected.sort(key=lambda i: i.occurred_at, reverse=True)
        return selected[:limit]
