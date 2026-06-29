import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.auth_deps import get_access_context
from app.api.deps import get_employee_service
from app.core.access_scope import AccessContext
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee_service import EmployeeService

router = APIRouter()


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    data: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponse:
    return service.create(data)


@router.get("", response_model=EmployeeListResponse)
def list_employees(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    department_id: uuid.UUID | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    scope: AccessContext = Depends(get_access_context),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeListResponse:
    return service.list(
        page=page,
        page_size=page_size,
        department_id=department_id,
        is_active=is_active,
        search=search,
        scope=scope,
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: uuid.UUID,
    scope: AccessContext = Depends(get_access_context),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponse:
    return service.get_by_id(employee_id, scope)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: uuid.UUID,
    data: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponse:
    return service.update(employee_id, data)


@router.delete("/{employee_id}", response_model=EmployeeResponse)
def deactivate_employee(
    employee_id: uuid.UUID,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponse:
    return service.deactivate(employee_id)
