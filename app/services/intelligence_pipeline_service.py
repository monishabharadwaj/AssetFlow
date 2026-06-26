from __future__ import annotations



import uuid

from datetime import datetime, timezone



from app.core.config import settings

from app.core.enums import NotificationSeverity, NotificationType

from app.schemas.operations import PipelineRunResponse, PipelineStatusResponse

from app.services.drift_monitoring_service import DriftMonitoringService

from app.services.policy_automation_service import PolicyAutomationService

from app.services.prediction_service import PredictionService, get_prediction_cache



_LAST_RUN_AT: datetime | None = None





def get_last_pipeline_run() -> datetime | None:

    return _LAST_RUN_AT





class IntelligencePipelineService:

    def __init__(

        self,

        prediction_service: PredictionService,

        drift_service: DriftMonitoringService,

        policy_service: PolicyAutomationService,

    ) -> None:

        self.prediction_service = prediction_service

        self.drift_service = drift_service

        self.policy_service = policy_service



    def run_full_pipeline(self, *, persist: bool = True) -> PipelineRunResponse:

        global _LAST_RUN_AT



        batch = self.prediction_service.score_batch(persist=persist)

        drift = self.drift_service.detect_drift()

        policy_result = self.policy_service.run_policies()

        escalation_count = self.policy_service.emit_escalation_notifications()

        positive_count = self.policy_service.emit_positive_notifications()



        drift_items = [

            {

                "notification_type": NotificationType.HEALTH_DRIFT,

                "severity": NotificationSeverity.HIGH,

                "title": f"Health drift — {alert.asset_tag}",

                "message": alert.message,

                "asset_id": uuid.UUID(alert.asset_id),

            }

            for alert in drift.alerts[:10]

        ]

        drift_notifications = self.policy_service.notification_service.create_many(drift_items)



        _LAST_RUN_AT = datetime.now(timezone.utc)

        total_notifications = (

            policy_result["notifications_created"]

            + escalation_count

            + drift_notifications

            + positive_count

        )



        return PipelineRunResponse(

            scored=batch.scored,

            failed=batch.failed,

            notifications_created=total_notifications,

            maintenance_auto_scheduled=policy_result["maintenance_auto_scheduled"],

            drift_alerts=len(drift.alerts),

            ran_at=_LAST_RUN_AT,

        )



    def get_status(self) -> PipelineStatusResponse:

        cache = get_prediction_cache()

        return PipelineStatusResponse(

            scheduler_enabled=settings.scheduler_enabled,

            scheduler_interval_minutes=settings.scheduler_interval_minutes,

            last_run_at=get_last_pipeline_run(),

            cache_warm=bool(cache),

            scored_assets=len(cache),

            policy_automation_enabled=settings.policy_automation_enabled,

        )

