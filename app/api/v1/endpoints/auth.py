from fastapi import APIRouter, Depends, status

from app.api.auth_deps import get_auth_service, get_current_user, require_roles
from app.core.enums import UserRole
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetResponse,
    TokenResponse,
    UserAdminUpdate,
    UserCreate,
    UserCreateResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return service.login(data)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return service.get_user(current_user.id)


@router.post("/change-password", response_model=UserResponse)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return service.change_password(current_user, data)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _admin: User = Depends(require_roles(UserRole.ADMIN)),
    service: AuthService = Depends(get_auth_service),
) -> list[UserResponse]:
    return service.list_users()


@router.post("/users", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    _admin: User = Depends(require_roles(UserRole.ADMIN)),
    service: AuthService = Depends(get_auth_service),
) -> UserCreateResponse:
    return service.create_user(data)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    data: UserAdminUpdate,
    _admin: User = Depends(require_roles(UserRole.ADMIN)),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    from uuid import UUID

    return service.update_user_admin(UUID(user_id), data)


@router.post("/users/{user_id}/reset-password", response_model=PasswordResetResponse)
def reset_user_password(
    user_id: str,
    _admin: User = Depends(require_roles(UserRole.ADMIN)),
    service: AuthService = Depends(get_auth_service),
) -> PasswordResetResponse:
    from uuid import UUID

    user, temporary_password = service.reset_password(UUID(user_id))
    return PasswordResetResponse(user=user, temporary_password=temporary_password)
