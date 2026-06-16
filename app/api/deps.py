from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.allocation_repository import AllocationRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.health_history_repository import HealthHistoryRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.transfer_repository import TransferRepository
from app.services.allocation_service import AllocationService
from app.services.asset_service import AssetService
from app.services.department_service import DepartmentService
from app.services.employee_service import EmployeeService
from app.services.health_history_service import HealthHistoryService
from app.services.maintenance_service import MaintenanceService
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
