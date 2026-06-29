from fastapi import APIRouter, Depends

from app.api.auth_deps import enforce_rbac
from app.api.v1.endpoints import (
    allocations,
    assets,
    assistant,
    auth,
    dashboard,
    departments,
    employees,
    health_history,
    intelligence,
    lookups,
    maintenance,
    operations,
    timeline,
    transfers,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

protected_router = APIRouter(dependencies=[Depends(enforce_rbac)])
protected_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
protected_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
protected_router.include_router(lookups.router, tags=["Asset Lookups"])
protected_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
protected_router.include_router(allocations.router, tags=["Asset Allocations"])
protected_router.include_router(transfers.router, tags=["Asset Transfers"])
protected_router.include_router(maintenance.router, tags=["Maintenance"])
protected_router.include_router(health_history.router, tags=["Asset Health History"])
protected_router.include_router(dashboard.router, tags=["Dashboard"])
protected_router.include_router(timeline.router, tags=["Asset Timeline"])
protected_router.include_router(intelligence.router, tags=["Intelligence"])
protected_router.include_router(assistant.router, tags=["Assistant"])
protected_router.include_router(operations.router, tags=["Operations"])
api_router.include_router(protected_router)

