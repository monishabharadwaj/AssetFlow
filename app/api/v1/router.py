from fastapi import APIRouter

from app.api.v1.endpoints import (
    allocations,
    assets,
    departments,
    employees,
    health_history,
    lookups,
    maintenance,
    transfers,
)

api_router = APIRouter()
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(lookups.router, tags=["Asset Lookups"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(allocations.router, tags=["Asset Allocations"])
api_router.include_router(transfers.router, tags=["Asset Transfers"])
api_router.include_router(maintenance.router, tags=["Maintenance"])
api_router.include_router(health_history.router, tags=["Asset Health History"])
