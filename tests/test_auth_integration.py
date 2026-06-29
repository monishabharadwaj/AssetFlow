"""Integration tests requiring PostgreSQL. Run with: pytest -m integration"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.core.enums import UserRole
from app.core.security import hash_password
from app.models.asset import Asset
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User

TEST_PASSWORD = "TempPass123!"
NEW_PASSWORD = "SecurePass456!"
TEST_EMAIL_DOMAIN = "@auth-test.assetflow.app"


@dataclass
class AuthTestAccount:
    user_id: uuid.UUID
    email: str
    department_id: uuid.UUID


def _cleanup(db) -> None:
    emails = list(
        db.execute(
            select(Employee.email).where(Employee.email.like(f"%{TEST_EMAIL_DOMAIN}"))
        ).scalars()
    )
    if not emails:
        return
    employee_ids = list(
        db.execute(select(Employee.id).where(Employee.email.in_(emails))).scalars()
    )
    if employee_ids:
        db.execute(delete(User).where(User.employee_id.in_(employee_ids)))
        db.execute(delete(Employee).where(Employee.id.in_(employee_ids)))
        db.commit()


def _provision(db, suffix: str, role: UserRole, dept_code: str) -> AuthTestAccount:
    dept = db.execute(select(Department).where(Department.code == dept_code)).scalar_one()
    email = f"{suffix}{TEST_EMAIL_DOMAIN}"
    employee = Employee(
        department_id=dept.id,
        employee_code=f"TEST-AUTH-{suffix.upper()}",
        first_name="Auth",
        last_name=f"Test {suffix}",
        email=email,
        job_title="Tester",
        is_active=True,
    )
    db.add(employee)
    db.flush()
    user = User(
        employee_id=employee.id,
        hashed_password=hash_password(TEST_PASSWORD),
        role=role,
        is_active=True,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    return AuthTestAccount(user_id=user.id, email=email, department_id=dept.id)


def _login(client: TestClient, email: str, password: str) -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        _cleanup(session)
        session.close()


@pytest.mark.integration
def test_first_login_password_change_flow(client: TestClient, db) -> None:
    _cleanup(db)
    account = _provision(db, "it-viewer", UserRole.VIEWER, "IT")

    login = client.post(
        "/api/v1/auth/login",
        json={"email": account.email, "password": TEST_PASSWORD},
    )
    assert login.status_code == 200
    assert login.json()["must_change_password"] is True

    headers = _login(client, account.email, TEST_PASSWORD)
    blocked = client.get("/api/v1/assets", headers=headers)
    assert blocked.status_code == 403

    change = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": TEST_PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert change.status_code == 200
    assert change.json()["must_change_password"] is False

    active_headers = _login(client, account.email, NEW_PASSWORD)
    assets = client.get("/api/v1/assets?is_active=true", headers=active_headers)
    assert assets.status_code == 200


@pytest.mark.integration
def test_department_asset_isolation(client: TestClient, db) -> None:
    _cleanup(db)
    it = _provision(db, "it-viewer", UserRole.VIEWER, "IT")
    fin = _provision(db, "fin-viewer", UserRole.VIEWER, "FIN")

    it_asset = db.execute(
        select(Asset.id)
        .join(Department, Asset.current_department_id == Department.id)
        .where(Department.code == "IT", Asset.is_active.is_(True))
        .limit(1)
    ).scalar_one_or_none()
    fin_asset = db.execute(
        select(Asset.id)
        .join(Department, Asset.current_department_id == Department.id)
        .where(Department.code == "FIN", Asset.is_active.is_(True))
        .limit(1)
    ).scalar_one_or_none()

    if it_asset is None or fin_asset is None:
        pytest.skip("Need IT and FIN assets in database")

    for account, password in ((fin, TEST_PASSWORD),):
        client.post(
            "/api/v1/auth/change-password",
            headers=_login(client, account.email, password),
            json={"current_password": TEST_PASSWORD, "new_password": NEW_PASSWORD},
        )
    fin_headers = _login(client, fin.email, NEW_PASSWORD)

    assert client.get(f"/api/v1/assets/{it_asset}", headers=fin_headers).status_code == 403
    assert client.get(f"/api/v1/assets/{fin_asset}", headers=fin_headers).status_code == 200
