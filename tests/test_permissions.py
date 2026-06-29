import pytest
from fastapi import HTTPException

from app.core.enums import UserRole
from app.core.permissions import assert_api_permission


class FakeUser:
    def __init__(self, role: UserRole) -> None:
        self.role = role


def _allows(user: FakeUser, method: str, path: str) -> bool:
    try:
        assert_api_permission(user, method, path)  # type: ignore[arg-type]
        return True
    except HTTPException:
        return False


def test_viewer_can_read_assets() -> None:
    assert _allows(FakeUser(UserRole.VIEWER), "GET", "/api/v1/assets")


def test_viewer_cannot_create_assets() -> None:
    assert not _allows(FakeUser(UserRole.VIEWER), "POST", "/api/v1/assets")


def test_manager_cannot_create_users() -> None:
    assert not _allows(FakeUser(UserRole.MANAGER), "POST", "/api/v1/auth/users")


def test_admin_can_create_users() -> None:
    assert _allows(FakeUser(UserRole.ADMIN), "POST", "/api/v1/auth/users")
