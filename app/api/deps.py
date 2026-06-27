from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.allocation_repository import AllocationRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.health_history_repository import HealthHistoryRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.timeline_repository import TimelineRepository
from app.repositories.transfer_repository import TransferRepository
from app.repositories.notification_repository import NotificationRepository
from app.services.allocation_service import AllocationService

from app.services.asset_service import AssetService
from app.services.assistant_service import AssistantService
from app.services.assistant_tools import AssistantTools
from app.services.dashboard_service import DashboardService
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService
from app.services.feature_engineering import FeatureEngineeringService
from app.services.health_history_service import HealthHistoryService
from app.services.maintenance_service import MaintenanceService
from app.services.notification_service import NotificationService
from app.services.cost_optimization_service import CostOptimizationService
from app.services.drift_monitoring_service import DriftMonitoringService
from app.services.replacement_planning_service import ReplacementPlanningService
from app.services.report_service import ReportService
from app.services.maintenance_scheduling_service import MaintenanceSchedulingService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.policy_automation_service import PolicyAutomationService
from app.services.intelligence_pipeline_service import IntelligencePipelineService

from app.services.prediction_explanation_service import PredictionExplanationService
from app.services.prediction_service import PredictionService
from app.services.recommendation_service import RecommendationService
from app.services.root_cause_service import RootCauseService
from app.services.timeline_service import TimelineService
from app.services.transfer_service import TransferService



def get_department_repository(db: Session = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)


def get_department_service(
    repository: DepartmentRepository = Depends(get_department_repository),
) -> DepartmentService:
    return DepartmentService(repository)


def get_employee_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    return EmployeeRepository(db)


def get_employee_service(
    repository: EmployeeRepository = Depends(get_employee_repository),
    department_service: DepartmentService = Depends(get_department_service),
) -> EmployeeService:
    return EmployeeService(repository, department_service)


def get_asset_repository(db: Session = Depends(get_db)) -> AssetRepository:
    return AssetRepository(db)


def get_asset_service(
    repository: AssetRepository = Depends(get_asset_repository),
    department_service: DepartmentService = Depends(get_department_service),
) -> AssetService:
    return AssetService(repository, department_service)


def get_allocation_repository(db: Session = Depends(get_db)) -> AllocationRepository:
    return AllocationRepository(db)


def get_allocation_service(
    repository: AllocationRepository = Depends(get_allocation_repository),
    asset_service: AssetService = Depends(get_asset_service),
    employee_service: EmployeeService = Depends(get_employee_service),
) -> AllocationService:
    return AllocationService(repository, asset_service, employee_service)


def get_transfer_repository(db: Session = Depends(get_db)) -> TransferRepository:
    return TransferRepository(db)


def get_transfer_service(
    repository: TransferRepository = Depends(get_transfer_repository),
    asset_service: AssetService = Depends(get_asset_service),
    department_service: DepartmentService = Depends(get_department_service),
) -> TransferService:
    return TransferService(repository, asset_service, department_service)


def get_maintenance_repository(db: Session = Depends(get_db)) -> MaintenanceRepository:
    return MaintenanceRepository(db)


def get_maintenance_service(
    repository: MaintenanceRepository = Depends(get_maintenance_repository),
    asset_service: AssetService = Depends(get_asset_service),
) -> MaintenanceService:
    return MaintenanceService(repository, asset_service)


def get_health_history_repository(db: Session = Depends(get_db)) -> HealthHistoryRepository:
    return HealthHistoryRepository(db)


def get_health_history_service(
    repository: HealthHistoryRepository = Depends(get_health_history_repository),
    asset_service: AssetService = Depends(get_asset_service),
) -> HealthHistoryService:
    return HealthHistoryService(repository, asset_service)


def get_dashboard_repository(db: Session = Depends(get_db)) -> DashboardRepository:
    return DashboardRepository(db)


def get_timeline_repository(db: Session = Depends(get_db)) -> TimelineRepository:
    return TimelineRepository(db)


def get_timeline_service(
    repository: TimelineRepository = Depends(get_timeline_repository),
    asset_service: AssetService = Depends(get_asset_service),
) -> TimelineService:
    return TimelineService(repository, asset_service)


def get_feature_engineering_service() -> FeatureEngineeringService:
    return FeatureEngineeringService()


def get_prediction_service(
    asset_service: AssetService = Depends(get_asset_service),
    feature_service: FeatureEngineeringService = Depends(get_feature_engineering_service),
    health_service: HealthHistoryService = Depends(get_health_history_service),
    asset_repository: AssetRepository = Depends(get_asset_repository),
) -> PredictionService:
    return PredictionService(asset_service, feature_service, health_service, asset_repository)


def get_dashboard_service(
    repository: DashboardRepository = Depends(get_dashboard_repository),
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> DashboardService:
    prediction_service.is_cache_warm()
    return DashboardService(repository)


def get_recommendation_service(
    prediction_service: PredictionService = Depends(get_prediction_service),
    dashboard_repository: DashboardRepository = Depends(get_dashboard_repository),
) -> RecommendationService:
    return RecommendationService(prediction_service, dashboard_repository)


def get_assistant_tools(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    asset_service: AssetService = Depends(get_asset_service),
    prediction_service: PredictionService = Depends(get_prediction_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    dashboard_repository: DashboardRepository = Depends(get_dashboard_repository),
) -> AssistantTools:
    return AssistantTools(
        dashboard_service,
        asset_service,
        prediction_service,
        recommendation_service,
        dashboard_repository,
    )


def get_assistant_service(
    tools: AssistantTools = Depends(get_assistant_tools),
) -> AssistantService:
    return AssistantService(tools)


def get_prediction_explanation_service() -> PredictionExplanationService:
    return PredictionExplanationService()


def get_root_cause_service(
    prediction_service: PredictionService = Depends(get_prediction_service),
    explanation_service: PredictionExplanationService = Depends(get_prediction_explanation_service),
    timeline_repository: TimelineRepository = Depends(get_timeline_repository),
) -> RootCauseService:
    return RootCauseService(
        prediction_service=prediction_service,
        explanation_service=explanation_service,
        timeline_repository=timeline_repository,
    )


def get_notification_repository(db: Session = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)


def get_notification_service(
    repository: NotificationRepository = Depends(get_notification_repository),
) -> NotificationService:
    return NotificationService(repository)


def get_cost_optimization_service(
    asset_repository: AssetRepository = Depends(get_asset_repository),
    maintenance_repository: MaintenanceRepository = Depends(get_maintenance_repository),
) -> CostOptimizationService:
    return CostOptimizationService(asset_repository, maintenance_repository)


def get_drift_monitoring_service(
    health_history_repository: HealthHistoryRepository = Depends(get_health_history_repository),
) -> DriftMonitoringService:
    return DriftMonitoringService(health_history_repository)


def get_replacement_planning_service(
    asset_repository: AssetRepository = Depends(get_asset_repository),
    maintenance_repository: MaintenanceRepository = Depends(get_maintenance_repository),
) -> ReplacementPlanningService:
    return ReplacementPlanningService(asset_repository, maintenance_repository)


def get_report_service(
    dashboard_repository: DashboardRepository = Depends(get_dashboard_repository),
    asset_repository: AssetRepository = Depends(get_asset_repository),
) -> ReportService:
    return ReportService(dashboard_repository, asset_repository)


def get_maintenance_scheduling_service(
    asset_repository: AssetRepository = Depends(get_asset_repository),
    maintenance_repository: MaintenanceRepository = Depends(get_maintenance_repository),
) -> MaintenanceSchedulingService:
    return MaintenanceSchedulingService(asset_repository, maintenance_repository)


def get_knowledge_graph_service(
    asset_repository: AssetRepository = Depends(get_asset_repository),
    department_repository: DepartmentRepository = Depends(get_department_repository),
) -> KnowledgeGraphService:
    return KnowledgeGraphService(asset_repository, department_repository)


def get_policy_automation_service(
    maintenance_repository: MaintenanceRepository = Depends(get_maintenance_repository),
    asset_repository: AssetRepository = Depends(get_asset_repository),
    dashboard_repository: DashboardRepository = Depends(get_dashboard_repository),
    notification_service: NotificationService = Depends(get_notification_service),
) -> PolicyAutomationService:
    return PolicyAutomationService(
        maintenance_repository,
        asset_repository,
        dashboard_repository,
        notification_service,
    )


def get_intelligence_pipeline_service(
    prediction_service: PredictionService = Depends(get_prediction_service),
    drift_service: DriftMonitoringService = Depends(get_drift_monitoring_service),
    policy_service: PolicyAutomationService = Depends(get_policy_automation_service),
) -> IntelligencePipelineService:
    return IntelligencePipelineService(
        prediction_service,
        drift_service,
        policy_service,
    )


