import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.api.auth_deps import get_access_context
from app.api.deps import (
    get_cost_optimization_service,
    get_drift_monitoring_service,
    get_intelligence_pipeline_service,
    get_knowledge_graph_service,
    get_maintenance_scheduling_service,
    get_notification_service,
    get_replacement_planning_service,
    get_report_service,
    get_reports_analytics_service,
)
from app.core.access_scope import AccessContext
from app.schemas.reports_analytics import ReportsAnalyticsResponse
from app.schemas.operations import (
    CostOptimizationResponse,
    DriftStatusResponse,
    KnowledgeGraphResponse,
    MaintenanceScheduleResponse,
    NotificationListResponse,
    NotificationResponse,
    OperationalReportResponse,
    PipelineRunResponse,
    PipelineStatusResponse,
    ReplacementPlanResponse,
)
from app.services.cost_optimization_service import CostOptimizationService
from app.services.drift_monitoring_service import DriftMonitoringService
from app.services.intelligence_pipeline_service import IntelligencePipelineService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.maintenance_scheduling_service import MaintenanceSchedulingService
from app.services.notification_service import NotificationService
from app.services.replacement_planning_service import ReplacementPlanningService
from app.services.report_service import ReportService
from app.services.reports_analytics_service import ReportsAnalyticsService

router = APIRouter()


def _department_id(scope: AccessContext) -> uuid.UUID | None:
    return scope.scoping_department_id()


@router.get("/operations/pipeline/status", response_model=PipelineStatusResponse)
def pipeline_status(
    service: IntelligencePipelineService = Depends(get_intelligence_pipeline_service),
) -> PipelineStatusResponse:
    return service.get_status()


@router.post("/operations/pipeline/run", response_model=PipelineRunResponse)
def run_pipeline(
    persist: bool = Query(default=True),
    service: IntelligencePipelineService = Depends(get_intelligence_pipeline_service),
) -> PipelineRunResponse:
    return service.run_full_pipeline(persist=persist)


@router.get("/operations/notifications", response_model=NotificationListResponse)
def list_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    unread_only: bool = Query(default=False),
    scope: AccessContext = Depends(get_access_context),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    return service.list_recent(limit=limit, unread_only=unread_only, scope=scope)


@router.patch("/operations/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    scope: AccessContext = Depends(get_access_context),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    result = service.mark_read(notification_id, scope)
    if result is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return result


@router.post("/operations/notifications/read-all")
def mark_all_notifications_read(
    scope: AccessContext = Depends(get_access_context),
    service: NotificationService = Depends(get_notification_service),
) -> dict[str, int]:
    return {"marked_read": service.mark_all_read(scope)}


@router.get("/operations/drift", response_model=DriftStatusResponse)
def drift_status(
    scope: AccessContext = Depends(get_access_context),
    service: DriftMonitoringService = Depends(get_drift_monitoring_service),
) -> DriftStatusResponse:
    return service.detect_drift(department_id=_department_id(scope))


@router.get("/operations/reports/weekly", response_model=OperationalReportResponse)
async def weekly_report(
    use_llm: bool = Query(default=False),
    scope: AccessContext = Depends(get_access_context),
    service: ReportService = Depends(get_report_service),
) -> OperationalReportResponse:
    return await service.generate_weekly_brief(use_llm=use_llm, scope=scope)


@router.get("/operations/reports/analytics", response_model=ReportsAnalyticsResponse)
async def reports_analytics(
    use_ai: bool = Query(default=False),
    scope: AccessContext = Depends(get_access_context),
    service: ReportsAnalyticsService = Depends(get_reports_analytics_service),
) -> ReportsAnalyticsResponse:
    return await service.build(use_ai=use_ai, scope=scope)


@router.get("/operations/replacement-plan", response_model=ReplacementPlanResponse)
def replacement_plan(
    limit: int = Query(default=15, ge=1, le=50),
    scope: AccessContext = Depends(get_access_context),
    service: ReplacementPlanningService = Depends(get_replacement_planning_service),
) -> ReplacementPlanResponse:
    return service.build_plan(limit=limit, department_id=_department_id(scope))


@router.get("/operations/cost-optimization", response_model=CostOptimizationResponse)
def cost_optimization(
    limit: int = Query(default=15, ge=1, le=50),
    scope: AccessContext = Depends(get_access_context),
    service: CostOptimizationService = Depends(get_cost_optimization_service),
) -> CostOptimizationResponse:
    return service.analyze(limit=limit, department_id=_department_id(scope))


@router.get("/operations/maintenance-schedule", response_model=MaintenanceScheduleResponse)
def maintenance_schedule(
    limit: int = Query(default=10, ge=1, le=50),
    scope: AccessContext = Depends(get_access_context),
    service: MaintenanceSchedulingService = Depends(get_maintenance_scheduling_service),
) -> MaintenanceScheduleResponse:
    return service.suggest_windows(limit=limit, department_id=_department_id(scope))


@router.get("/operations/graph/assets/{asset_id}", response_model=KnowledgeGraphResponse)
def asset_graph(
    asset_id: uuid.UUID,
    service: KnowledgeGraphService = Depends(get_knowledge_graph_service),
) -> KnowledgeGraphResponse:
    return service.asset_neighborhood(asset_id)


@router.get(
    "/operations/graph/departments/{department_id}/high-risk",
    response_model=KnowledgeGraphResponse,
)
def department_high_risk_graph(
    department_id: uuid.UUID,
    service: KnowledgeGraphService = Depends(get_knowledge_graph_service),
) -> KnowledgeGraphResponse:
    return service.department_high_risk(department_id)


@router.get("/operations/events/stream")
async def events_stream() -> StreamingResponse:
    import asyncio
    import json
    from datetime import datetime, timezone

    from app.core.database import SessionLocal
    from app.repositories.notification_repository import NotificationRepository

    async def generate():
        while True:
            db = SessionLocal()
            try:
                repo = NotificationRepository(db)
                items = repo.list_recent(limit=5, unread_only=True)
                payload = {
                    "type": "notifications",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "unread_count": repo.count_unread(),
                    "items": [
                        {
                            "id": str(n.id),
                            "title": n.title,
                            "severity": n.severity.value,
                            "notification_type": n.notification_type.value,
                        }
                        for n in items
                    ],
                }
            finally:
                db.close()
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(10)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
