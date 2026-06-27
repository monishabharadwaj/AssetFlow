from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select

from app.models.asset import Asset
from app.models.department import Department
from app.models.employee import Employee
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    def create(self, department: Department) -> Department:
        self.add(department)
        self.flush()
        return department

    def get_by_id(self, department_id: uuid.UUID) -> Department | None:
        return self.db.get(Department, department_id)

    def get_by_code(self, code: str) -> Department | None:
        stmt = select(Department).where(Department.code == code)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        *,
        page: int,
        page_size: int,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[Department], int]:
        stmt = select(Department)
        count_stmt = select(func.count()).select_from(Department)

        if is_active is not None:
            stmt = stmt.where(Department.is_active == is_active)
            count_stmt = count_stmt.where(Department.is_active == is_active)

        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                Department.name.ilike(pattern),
                Department.code.ilike(pattern),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = self.db.execute(count_stmt).scalar_one()
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Department.name).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def update(self, department: Department, data: dict) -> Department:
        return self.apply_partial_update(department, data)

    def count_active_employees(self, department_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Employee)
            .where(
                Employee.department_id == department_id,
                Employee.is_active.is_(True),
            )
        )
        return self.db.execute(stmt).scalar_one()

    def count_active_assets(self, department_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Asset)
            .where(
                Asset.current_department_id == department_id,
                Asset.is_active.is_(True),
            )
        )
        return self.db.execute(stmt).scalar_one()

    def find_best_match(self, query: str) -> Department | None:
        items, _ = self.list(page=1, page_size=1, is_active=True, search=query)
        return items[0] if items else None
