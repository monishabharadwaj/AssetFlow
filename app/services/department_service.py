from __future__ import annotations

import uuid

from app.core.access_scope import AccessContext
from app.exceptions.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.common import PaginatedResponse
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate


class DepartmentService:
    def __init__(self, repository: DepartmentRepository) -> None:
        self.repository = repository

    def create(self, data: DepartmentCreate) -> DepartmentResponse:
        code = data.code.upper()
        if self.repository.get_by_code(code):
            raise ConflictError(f"Department with code '{code}' already exists")

        department = Department(
            name=data.name,
            code=code,
            description=data.description,
            is_active=True,
        )
        self.repository.create(department)
        self.repository.commit()
        self.repository.refresh(department)
        return DepartmentResponse.model_validate(department)

    def get_by_id(self, department_id: uuid.UUID, scope: AccessContext | None = None) -> DepartmentResponse:
        department = self.repository.get_by_id(department_id)
        if not department:
            raise NotFoundError("Department", str(department_id))
        if scope is not None:
            scope.assert_department_access(department_id)
        return DepartmentResponse.model_validate(department)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        is_active: bool | None = None,
        search: str | None = None,
        scope: AccessContext | None = None,
    ) -> PaginatedResponse[DepartmentResponse]:
        if scope is not None:
            scoped = scope.scoping_department_id()
            if scoped is not None:
                department = self.repository.get_by_id(scoped)
                if department is None:
                    return PaginatedResponse.create(items=[], total=0, page=page, page_size=page_size)
                return PaginatedResponse.create(
                    items=[DepartmentResponse.model_validate(department)],
                    total=1,
                    page=1,
                    page_size=page_size,
                )
        items, total = self.repository.list(
            page=page,
            page_size=page_size,
            is_active=is_active,
            search=search,
        )
        return PaginatedResponse.create(
            items=[DepartmentResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, department_id: uuid.UUID, data: DepartmentUpdate) -> DepartmentResponse:
        department = self.repository.get_by_id(department_id)
        if not department:
            raise NotFoundError("Department", str(department_id))

        update_data = data.model_dump(exclude_unset=True)

        if "code" in update_data:
            code = update_data["code"].upper()
            existing = self.repository.get_by_code(code)
            if existing and existing.id != department_id:
                raise ConflictError(f"Department with code '{code}' already exists")
            update_data["code"] = code

        if update_data.get("is_active") is True and not department.is_active:
            self._ensure_can_reactivate(department_id)

        self.repository.update(department, update_data)
        self.repository.commit()
        self.repository.refresh(department)
        return DepartmentResponse.model_validate(department)

    def deactivate(self, department_id: uuid.UUID) -> DepartmentResponse:
        department = self.repository.get_by_id(department_id)
        if not department:
            raise NotFoundError("Department", str(department_id))

        if not department.is_active:
            return DepartmentResponse.model_validate(department)

        employee_count = self.repository.count_active_employees(department_id)
        asset_count = self.repository.count_active_assets(department_id)
        if employee_count > 0 or asset_count > 0:
            raise BusinessRuleError(
                f"Cannot deactivate department with {employee_count} active employee(s) "
                f"and {asset_count} active asset(s)"
            )

        department.is_active = False
        self.repository.commit()
        self.repository.refresh(department)
        return DepartmentResponse.model_validate(department)

    def _ensure_can_reactivate(self, department_id: uuid.UUID) -> None:
        # Reactivation is always allowed; dependencies do not block it.
        return

    def get_active_department(self, department_id: uuid.UUID) -> Department:
        department = self.repository.get_by_id(department_id)
        if not department:
            raise NotFoundError("Department", str(department_id))
        if not department.is_active:
            raise BusinessRuleError("Department is inactive")
        return department
