from fastapi import APIRouter, Depends, status

from app.api.auth_deps import get_auth_service, get_current_user, require_roles
from app.core.enums import UserRole
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
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


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _admin: User = Depends(require_roles(UserRole.ADMIN)),
    service: AuthService = Depends(get_auth_service),
) -> list[UserResponse]:
    return service.list_users()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    _admin: User = Depends(require_roles(UserRole.ADMIN)),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return service.create_user(data)
