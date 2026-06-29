from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task | None = None


def _run_pipeline_sync() -> None:
    from app.repositories.asset_repository import AssetRepository
    from app.repositories.dashboard_repository import DashboardRepository
    from app.repositories.department_repository import DepartmentRepository
    from app.repositories.health_history_repository import HealthHistoryRepository
    from app.repositories.maintenance_repository import MaintenanceRepository
    from app.repositories.notification_repository import NotificationRepository
    from app.services.asset_service import AssetService
    from app.services.department_service import DepartmentService
    from app.services.drift_monitoring_service import DriftMonitoringService
    from app.services.feature_engineering import FeatureEngineeringService
    from app.services.health_history_service import HealthHistoryService
    from app.services.intelligence_pipeline_service import IntelligencePipelineService
    from app.services.notification_service import NotificationService
    from app.services.policy_automation_service import PolicyAutomationService
    from app.services.prediction_explanation_service import PredictionExplanationService
    from app.services.prediction_service import PredictionService

    db = SessionLocal()
    try:
        asset_repo = AssetRepository(db)
        dept_repo = DepartmentRepository(db)
        health_repo = HealthHistoryRepository(db)
        maint_repo = MaintenanceRepository(db)
        dash_repo = DashboardRepository(db)
        notif_repo = NotificationRepository(db)

        dept_service = DepartmentService(dept_repo)
        asset_service = AssetService(asset_repo, dept_service)
        health_service = HealthHistoryService(health_repo, asset_service)
        notif_service = NotificationService(notif_repo, asset_repo)
        prediction_service = PredictionService(
            asset_service,
            FeatureEngineeringService(),
            health_service,
            asset_repo,
            health_repo,
            PredictionExplanationService(),
        )
        pipeline = IntelligencePipelineService(
            prediction_service,
            DriftMonitoringService(health_repo, asset_repo),
            PolicyAutomationService(
                maint_repo,
                asset_repo,
                dash_repo,
                notif_service,
            ),
        )
        result = pipeline.run_full_pipeline(persist=True)
        logger.info(
            "Scheduled AI pipeline completed: scored=%s notifications=%s",
            result.scored,
            result.notifications_created,
        )
    except Exception:
        logger.exception("Scheduled AI pipeline failed")
    finally:
        db.close()


async def _scheduler_loop() -> None:
    interval = max(5, settings.scheduler_interval_minutes) * 60
    if settings.scheduler_run_on_startup:
        await asyncio.to_thread(_run_pipeline_sync)
    while True:
        await asyncio.sleep(interval)
        await asyncio.to_thread(_run_pipeline_sync)


@asynccontextmanager
async def lifespan_scheduler(app):  # noqa: ARG001
    global _scheduler_task
    if settings.scheduler_enabled and settings.ml_enabled:
        _scheduler_task = asyncio.create_task(_scheduler_loop())
        logger.info(
            "AI scheduler started (interval=%s min)",
            settings.scheduler_interval_minutes,
        )
    yield
    if _scheduler_task is not None:
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
