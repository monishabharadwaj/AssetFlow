from __future__ import annotations

import uuid

from app.core.access_scope import AccessContext
from app.exceptions.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.common import PaginatedResponse
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.department_service import DepartmentService


class EmployeeService:
    def __init__(
        self,
        repository: EmployeeRepository,
        department_service: DepartmentService,
    ) -> None:
        self.repository = repository
        self.department_service = department_service

    def create(self, data: EmployeeCreate) -> EmployeeResponse:
        self.department_service.get_active_department(data.department_id)

        if self.repository.get_by_code(data.employee_code):
            raise ConflictError(f"Employee with code '{data.employee_code}' already exists")
        if self.repository.get_by_email(str(data.email)):
            raise ConflictError(f"Employee with email '{data.email}' already exists")

        employee = Employee(
            department_id=data.department_id,
            employee_code=data.employee_code,
            first_name=data.first_name,
            last_name=data.last_name,
            email=str(data.email),
            job_title=data.job_title,
            is_active=True,
        )
        self.repository.create(employee)
        self.repository.commit()
        self.repository.refresh(employee)
        return EmployeeResponse.model_validate(employee)

    def get_by_id(self, employee_id: uuid.UUID, scope: AccessContext | None = None) -> EmployeeResponse:
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee", str(employee_id))
        if scope is not None:
            scope.assert_department_access(employee.department_id)
        return EmployeeResponse.model_validate(employee)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        department_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        scope: AccessContext | None = None,
    ) -> PaginatedResponse[EmployeeResponse]:
        if scope is not None:
            scoped = scope.scoping_department_id()
            if scoped is not None:
                if department_id is not None and department_id != scoped:
                    raise BusinessRuleError("You do not have access to employees in that department")
                department_id = scoped
        items, total = self.repository.list(
            page=page,
            page_size=page_size,
            department_id=department_id,
            is_active=is_active,
            search=search,
        )
        return PaginatedResponse.create(
            items=[EmployeeResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, employee_id: uuid.UUID, data: EmployeeUpdate) -> EmployeeResponse:
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee", str(employee_id))

        update_data = data.model_dump(exclude_unset=True)

        if "department_id" in update_data:
            self.department_service.get_active_department(update_data["department_id"])

        if "employee_code" in update_data:
            existing = self.repository.get_by_code(update_data["employee_code"])
            if existing and existing.id != employee_id:
                raise ConflictError(
                    f"Employee with code '{update_data['employee_code']}' already exists"
                )

        if "email" in update_data:
            email = str(update_data["email"])
            existing = self.repository.get_by_email(email)
            if existing and existing.id != employee_id:
                raise ConflictError(f"Employee with email '{email}' already exists")
            update_data["email"] = email

        self.repository.update(employee, update_data)
        self.repository.commit()
        self.repository.refresh(employee)
        return EmployeeResponse.model_validate(employee)

    def deactivate(self, employee_id: uuid.UUID) -> EmployeeResponse:
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee", str(employee_id))

        if not employee.is_active:
            return EmployeeResponse.model_validate(employee)

        assigned_count = self.repository.count_assigned_assets(employee_id)
        if assigned_count > 0:
            raise BusinessRuleError(
                f"Cannot deactivate employee with {assigned_count} currently assigned asset(s)"
            )

        employee.is_active = False
        self.repository.commit()
        self.repository.refresh(employee)
        return EmployeeResponse.model_validate(employee)

    def get_active_employee(self, employee_id: uuid.UUID) -> Employee:
        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise NotFoundError("Employee", str(employee_id))
        if not employee.is_active:
            raise BusinessRuleError("Employee is inactive")
        return employee
