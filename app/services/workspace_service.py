from __future__ import annotations

from app.core.access_scope import AccessContext
from app.repositories.asset_repository import AssetRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.workspace import (
    MyAssetItem,
    MyMaintenanceItem,
    MyNotificationItem,
    MyWorkspaceResponse,
)


class WorkspaceService:
    def __init__(
        self,
        dashboard_repository: DashboardRepository,
        asset_repository: AssetRepository,
        notification_repository: NotificationRepository,
        employee_repository: EmployeeRepository,
    ) -> None:
        self.dashboard_repository = dashboard_repository
        self.asset_repository = asset_repository
        self.notification_repository = notification_repository
        self.employee_repository = employee_repository

    def get_my_workspace(self, scope: AccessContext) -> MyWorkspaceResponse:
        employee = self.employee_repository.get_by_id(scope.employee_id)
        if employee is None:
            raise ValueError("Employee not found for current user")

        assigned = self.dashboard_repository.list_assigned_assets(scope.employee_id, limit=20)
        asset_ids = [asset.id for asset in assigned]
        type_names = self.asset_repository.get_type_names_for_assets(asset_ids)

        maintenance_rows = self.dashboard_repository.list_upcoming_maintenance_for_assets(
            asset_ids, limit=10
        )
        notifications = self.notification_repository.list_for_assets(asset_ids, limit=10)

        department_name = employee.department.name if employee.department else ""
        dept_filter = scope.scoping_department_id() or scope.department_id
        dept_asset_count = self.dashboard_repository.count_assets(
            active_only=True,
            department_id=dept_filter,
        )

        return MyWorkspaceResponse(
            full_name=employee.full_name,
            department_name=department_name,
            role=scope.role,
            assigned_assets=[
                MyAssetItem(
                    id=asset.id,
                    asset_tag=asset.asset_tag,
                    name=asset.name,
                    current_status=asset.current_status.value,
                    asset_type_name=type_names.get(str(asset.id)),
                )
                for asset in assigned
            ],
            upcoming_maintenance=[
                MyMaintenanceItem(
                    asset_id=asset.id,
                    asset_tag=asset.asset_tag,
                    maintenance_type=record.maintenance_type.value,
                    scheduled_date=record.scheduled_date,
                    status=record.status.value,
                    description=record.description,
                )
                for record, asset in maintenance_rows
            ],
            notifications=[
                MyNotificationItem(
                    id=item.id,
                    title=item.title,
                    severity=item.severity.value,
                    message=item.message,
                    asset_id=item.asset_id,
                    created_at=item.created_at,
                )
                for item in notifications
            ],
            department_asset_count=dept_asset_count,
        )
