from __future__ import annotations

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.enums import UserRole
from app.core.permissions import assert_api_permission
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

_bearer = HTTPBearer(auto_error=False)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_employee_repository(db: Session = Depends(get_db)) -> EmployeeRepository:
    return EmployeeRepository(db)


def get_department_repository_for_auth(db: Session = Depends(get_db)) -> DepartmentRepository:
    return DepartmentRepository(db)


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
    employee_repository: EmployeeRepository = Depends(get_employee_repository),
    department_repository: DepartmentRepository = Depends(get_department_repository_for_auth),
) -> AuthService:
    return AuthService(repository, employee_repository, department_repository)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Session = Depends(get_db),
) -> User:
    if not settings.auth_enabled:
        users = UserRepository(db).list_all()
        if users:
            return users[0]
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is disabled but no users exist in the database",
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def enforce_rbac(
    request: Request,
    user: User = Depends(get_current_user),
) -> User:
    assert_api_permission(user, request.method, request.url.path)
    return user


def require_roles(*roles: UserRole):
    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this action",
            )
        return user

    return _checker
