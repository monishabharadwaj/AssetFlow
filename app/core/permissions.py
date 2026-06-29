"""Role-based access control for API routes."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.enums import UserRole
from app.models.user import User

# Organizational admin — admin role only.
_ADMIN_WRITE_PREFIXES = (
    "/departments",
    "/employees",
    "/auth/users",
)

# Operational writes — admin and manager.
_MANAGER_WRITE_PREFIXES = (
    "/assets",
    "/allocations",
    "/transfers",
    "/maintenance",
    "/health",
    "/intelligence/assets/",
    "/intelligence/score-batch",
    "/operations/pipeline/run",
    "/operations/notifications/read-all",
)

# Read-like POST endpoints available to viewers.
_VIEWER_POST_SUFFIXES = ("/assistant/chat",)

# Soft mutations viewers may perform.
_VIEWER_PATCH_FRAGMENTS = ("/operations/notifications/",)


def normalize_api_path(path: str) -> str:
    if path.startswith("/api/v1"):
        return path[len("/api/v1") :]
    return path


def assert_api_permission(user: User, method: str, path: str) -> None:
    if not settings.auth_enabled:
        return

    rel = normalize_api_path(path)
    role = user.role

    if role == UserRole.ADMIN:
        return

    if method == "GET":
        return

    if role == UserRole.VIEWER:
        if method == "POST" and any(rel.endswith(suffix) for suffix in _VIEWER_POST_SUFFIXES):
            return
        if method == "PATCH" and any(fragment in rel for fragment in _VIEWER_PATCH_FRAGMENTS):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers have read-only access",
        )

    if role == UserRole.MANAGER:
        if method in ("POST", "PUT", "PATCH", "DELETE") and any(
            rel.startswith(prefix) or rel.startswith(f"{prefix}/") for prefix in _ADMIN_WRITE_PREFIXES
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Managers cannot modify organizational or user-administration data",
            )
        if method == "POST" and any(rel.endswith(suffix) for suffix in _VIEWER_POST_SUFFIXES):
            return
        if method == "PATCH" and any(fragment in rel for fragment in _VIEWER_PATCH_FRAGMENTS):
            return
        if method in ("POST", "PUT", "PATCH", "DELETE") and any(
            rel.startswith(prefix) for prefix in _MANAGER_WRITE_PREFIXES
        ):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers do not have permission for this action",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions for this action",
    )
