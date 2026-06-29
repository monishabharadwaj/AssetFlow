from __future__ import annotations

import uuid
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.core.enums import UserRole
from app.models.asset import Asset
from app.models.user import User


@dataclass(frozen=True)
class AccessContext:
    user_id: uuid.UUID
    employee_id: uuid.UUID
    role: UserRole
    department_id: uuid.UUID

    @property
    def is_org_wide(self) -> bool:
        return self.role == UserRole.ADMIN

    def scoping_department_id(self) -> uuid.UUID | None:
        return None if self.is_org_wide else self.department_id

    def can_access_department(self, department_id: uuid.UUID) -> bool:
        return self.is_org_wide or self.department_id == department_id

    def can_access_asset(self, asset: Asset) -> bool:
        if self.is_org_wide:
            return True
        return asset.current_department_id == self.department_id

    def assert_department_access(self, department_id: uuid.UUID) -> None:
        if not self.can_access_department(department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this department",
            )

    def assert_asset_access(self, asset: Asset) -> None:
        if not self.can_access_asset(asset):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this asset",
            )


def access_context_from_user(user: User) -> AccessContext:
    employee = user.employee
    return AccessContext(
        user_id=user.id,
        employee_id=employee.id,
        role=user.role,
        department_id=employee.department_id,
    )
