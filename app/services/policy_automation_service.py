from __future__ import annotations

import uuid
from datetime import date, timedelta

from app.core.config import settings
from app.core.enums import MaintenanceStatus, MaintenanceType, NotificationSeverity, NotificationType
from app.core.health_thresholds import should_notify_high_risk
from app.models.maintenance import MaintenanceRecord
from app.repositories.asset_repository import AssetRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.schemas.intelligence import RiskLevel
from app.services import narrative as narr
from app.services.notification_service import NotificationService
from app.services.prediction_service import get_prediction_cache

_CRITICAL_TYPES = {"Server", "Production Machine", "Networking Device", "UPS", "Delivery Van"}


class PolicyAutomationService:
    def __init__(
        self,
        maintenance_repository: MaintenanceRepository,
        asset_repository: AssetRepository,
        dashboard_repository: DashboardRepository,
        notification_service: NotificationService,
    ) -> None:
        self.maintenance_repository = maintenance_repository
        self.asset_repository = asset_repository
        self.dashboard_repository = dashboard_repository
        self.notification_service = notification_service

    def run_policies(self) -> dict[str, int]:
        if not settings.policy_automation_enabled:
            return {"maintenance_auto_scheduled": 0, "notifications_created": 0}

        maintenance_scheduled = 0
        pending_notifications: list[dict] = []
        max_auto_schedule = 15

        for prediction in get_prediction_cache().values():
            if maintenance_scheduled >= max_auto_schedule:
                break
            if prediction.risk_level != RiskLevel.HIGH:
                continue
            if not should_notify_high_risk(prediction.health_score):
                continue

            asset_id = uuid.UUID(prediction.asset_id)
            if self.maintenance_repository.has_open_maintenance(asset_id):
                continue

            asset_types = self.asset_repository.get_type_names_for_assets([asset_id])
            asset_type = asset_types.get(prediction.asset_id, "Laptop")
            features = prediction.prediction_metadata.get("input_features", {})
            failure_count = int(features.get("failure_count", 0))

            maint_type = MaintenanceType.INSPECTION if failure_count >= 2 else MaintenanceType.PREVENTIVE
            days_out = 3 if asset_type in _CRITICAL_TYPES else 7
            scheduled_date = date.today() + timedelta(days=days_out)

            asset_name = prediction.asset_name or prediction.asset_tag or "Asset"
            description = (
                f"Auto-scheduled by policy: {prediction.risk_level.value} risk "
                f"(health {int(prediction.health_score * 100)}%) for {asset_type}."
            )

            record = MaintenanceRecord(
                asset_id=asset_id,
                maintenance_type=maint_type,
                status=MaintenanceStatus.SCHEDULED,
                scheduled_date=scheduled_date,
                description=description,
            )
            self.maintenance_repository.create(record)
            maintenance_scheduled += 1

            pending_notifications.append(
                {
                    "notification_type": NotificationType.POLICY_AUTO_MAINTENANCE,
                    "severity": NotificationSeverity.HIGH,
                    "title": f"Auto-scheduled maintenance — {prediction.asset_tag}",
                    "message": narr.policy_auto_maintenance_message(
                        asset_name=asset_name,
                        maintenance_type=maint_type.value,
                        scheduled_date=scheduled_date,
                    ),
                    "asset_id": asset_id,
                }
            )

        self.maintenance_repository.commit()
        notifications_created = self.notification_service.create_many(pending_notifications)
        return {
            "maintenance_auto_scheduled": maintenance_scheduled,
            "notifications_created": notifications_created,
        }

    def emit_escalation_notifications(self) -> int:
        pending: list[dict] = []
        cache = get_prediction_cache()

        high_risk = sorted(
            [p for p in cache.values() if should_notify_high_risk(p.health_score)],
            key=lambda p: p.health_score,
        )[:5]

        for prediction in high_risk:
            asset_id = uuid.UUID(prediction.asset_id)
            asset_name = prediction.asset_name or prediction.asset_tag or "Asset"
            pending.append(
                {
                    "notification_type": NotificationType.HIGH_RISK,
                    "severity": NotificationSeverity.HIGH,
                    "title": f"High risk — {prediction.asset_tag}",
                    "message": narr.high_risk_attention_message(
                        asset_name=asset_name,
                        score=prediction.health_score,
                        risk_level=prediction.risk_level.value,
                    ),
                    "asset_id": asset_id,
                }
            )

        for asset in self.dashboard_repository.warranty_expiring_soon(within_days=30, limit=10):
            if asset.warranty_expiry is None:
                continue
            pending.append(
                {
                    "notification_type": NotificationType.WARRANTY_EXPIRING,
                    "severity": NotificationSeverity.MEDIUM,
                    "title": f"Warranty expiring — {asset.asset_tag}",
                    "message": narr.warranty_expiring_bullet(
                        asset_name=asset.name,
                        asset_tag=asset.asset_tag,
                        expiry=asset.warranty_expiry,
                    ),
                    "asset_id": asset.id,
                }
            )

        for record, asset in self.dashboard_repository.maintenance_due_items(limit=5):
            pending.append(
                {
                    "notification_type": NotificationType.MAINTENANCE_DUE,
                    "severity": NotificationSeverity.HIGH,
                    "title": f"Maintenance overdue — {asset.asset_tag}",
                    "message": narr.maintenance_attention_message(
                        asset_name=asset.name,
                        scheduled_date=record.scheduled_date,
                    ),
                    "asset_id": asset.id,
                }
            )

        return self.notification_service.create_many(pending)

    def emit_positive_notifications(self) -> int:
        """Celebrate operational improvements after fleet scoring."""
        pending: list[dict] = []
        cache = get_prediction_cache()

        for prediction in cache.values():
            explanation = prediction.explanation
            if not explanation or explanation.health_delta is None:
                continue
            if explanation.health_delta <= 0.05:
                continue
            asset_id = uuid.UUID(prediction.asset_id)
            asset_name = prediction.asset_name or prediction.asset_tag or "Asset"
            delta_pct = int(explanation.health_delta * 100)
            pending.append(
                {
                    "notification_type": NotificationType.HEALTH_IMPROVED,
                    "severity": NotificationSeverity.SUCCESS,
                    "title": f"Health improved — {prediction.asset_tag}",
                    "message": (
                        f"{asset_name} health improved by {delta_pct}% since the last assessment. "
                        "Continue the current maintenance schedule."
                    ),
                    "asset_id": asset_id,
                }
            )

        for record, asset in self.dashboard_repository.recent_completed_maintenance(limit=5):
            if record.maintenance_type.value == "INSPECTION":
                ntype = NotificationType.INSPECTION_PASSED
                title = f"Inspection passed — {asset.asset_tag}"
            else:
                ntype = NotificationType.MAINTENANCE_COMPLETED
                title = f"Maintenance completed — {asset.asset_tag}"
            pending.append(
                {
                    "notification_type": ntype,
                    "severity": NotificationSeverity.SUCCESS,
                    "title": title,
                    "message": (
                        f"{asset.name} {record.maintenance_type.value.lower()} "
                        "was completed successfully."
                    ),
                    "asset_id": asset.id,
                }
            )

        for row in self.dashboard_repository.recent_transfers(limit=3):
            asset = row.asset
            pending.append(
                {
                    "notification_type": NotificationType.TRANSFER_COMPLETED,
                    "severity": NotificationSeverity.INFO,
                    "title": f"Transfer completed — {asset.asset_tag}",
                    "message": (
                        f"{asset.name} was transferred to {row.to_department.name} successfully."
                    ),
                    "asset_id": asset.id,
                }
            )

        return self.notification_service.create_many(pending[:12])
