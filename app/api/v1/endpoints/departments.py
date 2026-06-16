import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_department_service
from app.schemas.department import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import DepartmentService

router = APIRouter()


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    data: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponse:
    return service.create(data)


@router.get("", response_model=DepartmentListResponse)
def list_departments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentListResponse:
    return service.list(page=page, page_size=page_size, is_active=is_active, search=search)


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: uuid.UUID,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponse:
    return service.get_by_id(department_id)


@router.patch("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: uuid.UUID,
    data: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponse:
    return service.update(department_id, data)


@router.delete("/{department_id}", response_model=DepartmentResponse)
def deactivate_department(
    department_id: uuid.UUID,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentResponse:
    return service.deactivate(department_id)
