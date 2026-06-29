from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.employee import Employee
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def create(self, user: User) -> User:
        self.add(user)
        self.flush()
        return user

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.employee).joinedload(Employee.department))
            .where(User.id == user_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_employee_id(self, employee_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.employee).joinedload(Employee.department))
            .where(User.employee_id == employee_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[User]:
        stmt = (
            select(User)
            .options(joinedload(User.employee).joinedload(Employee.department))
            .order_by(User.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().unique().all())
