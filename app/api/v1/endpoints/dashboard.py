from fastapi import APIRouter, Depends

from app.api.auth_deps import get_access_context
from app.api.deps import get_dashboard_service, get_workspace_service
from app.core.access_scope import AccessContext
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.workspace import MyWorkspaceResponse
from app.services.dashboard_service import DashboardService
from app.services.workspace_service import WorkspaceService

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    scope: AccessContext = Depends(get_access_context),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummaryResponse:
    return service.get_summary(scope)


@router.get("/dashboard/my-workspace", response_model=MyWorkspaceResponse)
def get_my_workspace(
    scope: AccessContext = Depends(get_access_context),
    service: WorkspaceService = Depends(get_workspace_service),
) -> MyWorkspaceResponse:
    return service.get_my_workspace(scope)
