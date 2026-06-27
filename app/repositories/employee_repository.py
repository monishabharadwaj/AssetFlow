from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select

from app.models.asset import Asset
from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def create(self, employee: Employee) -> Employee:
        self.add(employee)
        self.flush()
        return employee

    def get_by_id(self, employee_id: uuid.UUID) -> Employee | None:
        return self.db.get(Employee, employee_id)

    def get_by_code(self, employee_code: str) -> Employee | None:
        stmt = select(Employee).where(Employee.employee_code == employee_code)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> Employee | None:
        stmt = select(Employee).where(Employee.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        *,
        page: int,
        page_size: int,
        department_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Employee], int]:
        stmt = select(Employee)
        count_stmt = select(func.count()).select_from(Employee)

        if department_id is not None:
            stmt = stmt.where(Employee.department_id == department_id)
            count_stmt = count_stmt.where(Employee.department_id == department_id)

        if is_active is not None:
            stmt = stmt.where(Employee.is_active == is_active)
            count_stmt = count_stmt.where(Employee.is_active == is_active)

        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                Employee.first_name.ilike(pattern),
                Employee.last_name.ilike(pattern),
                Employee.email.ilike(pattern),
                Employee.employee_code.ilike(pattern),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Employee.last_name, Employee.first_name).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def update(self, employee: Employee, data: dict) -> Employee:
        return self.apply_partial_update(employee, data)

    def count_assigned_assets(self, employee_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Asset)
            .where(
                Asset.current_assigned_employee_id == employee_id,
                Asset.is_active.is_(True),
            )
        )
        return self.db.execute(stmt).scalar_one()

    def find_best_match(self, query: str) -> Employee | None:
        items, _ = self.list(page=1, page_size=1, is_active=True, search=query)
        return items[0] if items else None
