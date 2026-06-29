"""Create login accounts linked to seeded employees."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.core.security import hash_password
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.repositories.user_repository import UserRepository

DEFAULT_SEED_PASSWORD = "Welcome123"


def _role_for_employee(employee: Employee, dept_by_id: dict, admin_assigned: bool) -> tuple[UserRole, bool]:
    dept = dept_by_id.get(employee.department_id)
    dept_code = dept.code if dept else ""
    if employee.job_title == "Manager":
        if not admin_assigned and dept_code == "IT":
            return UserRole.ADMIN, True
        return UserRole.MANAGER, admin_assigned
    return UserRole.VIEWER, admin_assigned


def ensure_employee_accounts(db: Session, *, password: str = DEFAULT_SEED_PASSWORD) -> dict[str, int]:
    """Create one login account per active employee when missing."""
    repo = UserRepository(db)
    employees = list(db.execute(select(Employee).where(Employee.is_active.is_(True))).scalars().all())
    departments = list(db.execute(select(Department)).scalars().all())
    dept_by_id = {dept.id: dept for dept in departments}

    created = 0
    admin_assigned = False
    hashed = hash_password(password)

    for employee in sorted(employees, key=lambda e: e.employee_code):
        if repo.get_by_employee_id(employee.id) is not None:
            continue
        role, admin_assigned = _role_for_employee(employee, dept_by_id, admin_assigned)
        repo.create(
            User(
                employee_id=employee.id,
                hashed_password=hashed,
                role=role,
                is_active=True,
            )
        )
        created += 1

    if created:
        repo.commit()

    return {
        "accounts_created": created,
        "total_employees": len(employees),
        "default_password": password,
    }
