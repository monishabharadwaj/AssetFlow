"""
Auth & RBAC regression suite — run with:
  $env:PYTHONPATH='.'; py scratch/test_auth_rbac.py

Unit tests run without a server. Integration tests use TestClient against the
configured database (seeded enterprise profile recommended).
"""
from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from app.core.access_scope import AccessContext
from app.core.database import SessionLocal
from app.core.enums import UserRole
from app.core.password_policy import generate_temporary_password, validate_password_strength
from app.core.permissions import assert_api_permission
from app.core.security import hash_password
from app.main import app
from app.models.asset import Asset
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User

TEST_PASSWORD = "TempPass123!"
NEW_PASSWORD = "SecurePass456!"
WEAK_PASSWORD = "short"
TEST_EMAIL_DOMAIN = "@auth-test.assetflow.app"

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        suffix = f" — {detail}" if detail else ""
        print(f"FAIL: {name}{suffix}")


def expect_raises(name: str, exc_type: type[BaseException], fn) -> None:
    try:
        fn()
    except exc_type:
        check(name, True)
    except Exception as exc:
        check(name, False, f"expected {exc_type.__name__}, got {type(exc).__name__}: {exc}")
    else:
        check(name, False, f"expected {exc_type.__name__} but nothing was raised")


# ---------------------------------------------------------------------------
# Unit tests (no database required)
# ---------------------------------------------------------------------------


def test_password_policy() -> None:
    print("\n=== Password Policy ===")
    validate_password_strength(TEST_PASSWORD)
    check("accepts strong password", True)

    expect_raises(
        "rejects short password",
        ValueError,
        lambda: validate_password_strength(WEAK_PASSWORD),
    )
    expect_raises(
        "rejects missing uppercase",
        ValueError,
        lambda: validate_password_strength("lowercase1!"),
    )
    expect_raises(
        "rejects missing special character",
        ValueError,
        lambda: validate_password_strength("NoSpecial1"),
    )

    temp = generate_temporary_password()
    validate_password_strength(temp)
    check("generated temporary password satisfies policy", len(temp) >= 8)


def test_access_scope() -> None:
    print("\n=== Access Scope ===")
    dept_a = uuid.uuid4()
    dept_b = uuid.uuid4()
    admin = AccessContext(
        user_id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        role=UserRole.ADMIN,
        department_id=dept_a,
    )
    viewer = AccessContext(
        user_id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        role=UserRole.VIEWER,
        department_id=dept_a,
    )

    check("admin is org-wide", admin.is_org_wide)
    check("viewer is not org-wide", not viewer.is_org_wide)
    check("admin scoping returns None", admin.scoping_department_id() is None)
    check("viewer scoped to own department", viewer.scoping_department_id() == dept_a)
    check("viewer can access own department", viewer.can_access_department(dept_a))
    check("viewer cannot access other department", not viewer.can_access_department(dept_b))


def test_permissions_matrix() -> None:
    print("\n=== RBAC Permission Matrix ===")

    class FakeUser:
        def __init__(self, role: UserRole) -> None:
            self.role = role

    viewer = FakeUser(UserRole.VIEWER)
    manager = FakeUser(UserRole.MANAGER)
    admin = FakeUser(UserRole.ADMIN)

    def allows(user, method: str, path: str) -> bool:
        try:
            assert_api_permission(user, method, path)  # type: ignore[arg-type]
            return True
        except Exception:
            return False

    check("viewer can GET assets", allows(viewer, "GET", "/api/v1/assets"))
    check("viewer cannot POST assets", not allows(viewer, "POST", "/api/v1/assets"))
    check("viewer can use assistant chat", allows(viewer, "POST", "/api/v1/assistant/chat"))
    check("manager can POST assets", allows(manager, "POST", "/api/v1/assets"))
    check(
        "manager cannot create users",
        not allows(manager, "POST", "/api/v1/auth/users"),
    )
    check("admin can create users", allows(admin, "POST", "/api/v1/auth/users"))


# ---------------------------------------------------------------------------
# Integration helpers
# ---------------------------------------------------------------------------


@dataclass
class TestAccount:
    user_id: uuid.UUID
    employee_id: uuid.UUID
    email: str
    role: UserRole
    department_id: uuid.UUID
    department_code: str


def _cleanup_test_accounts(db) -> None:
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


def _provision_account(
    db,
    *,
    suffix: str,
    role: UserRole,
    dept_code: str,
    must_change_password: bool = True,
) -> TestAccount:
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
        must_change_password=must_change_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TestAccount(
        user_id=user.id,
        employee_id=employee.id,
        email=email,
        role=role,
        department_id=dept.id,
        department_code=dept_code,
    )


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        raise RuntimeError(f"login failed for {email}: {resp.status_code} {resp.text}")
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _asset_counts_by_department(db) -> dict[str, int]:
    rows = db.execute(
        select(Department.code, func.count(Asset.id))
        .join(Asset, Asset.current_department_id == Department.id)
        .where(Asset.is_active.is_(True))
        .group_by(Department.code)
    ).all()
    return {code: count for code, count in rows}


def _sample_asset_ids(db) -> dict[str, uuid.UUID]:
    result: dict[str, uuid.UUID] = {}
    for code in ("IT", "FIN", "HR"):
        asset_id = db.execute(
            select(Asset.id)
            .join(Department, Asset.current_department_id == Department.id)
            .where(Department.code == code, Asset.is_active.is_(True))
            .limit(1)
        ).scalar_one_or_none()
        if asset_id is not None:
            result[code] = asset_id
    return result


def test_integration() -> None:
    print("\n=== Integration (TestClient + database) ===")
    db = SessionLocal()
    client = TestClient(app)
    accounts: list[TestAccount] = []

    try:
        _cleanup_test_accounts(db)
        accounts = [
            _provision_account(db, suffix="it-viewer", role=UserRole.VIEWER, dept_code="IT"),
            _provision_account(db, suffix="fin-viewer", role=UserRole.VIEWER, dept_code="FIN"),
            _provision_account(
                db,
                suffix="it-admin",
                role=UserRole.ADMIN,
                dept_code="IT",
                must_change_password=False,
            ),
        ]
        asset_ids = _sample_asset_ids(db)
        dept_counts = _asset_counts_by_department(db)

        if "IT" not in asset_ids or "FIN" not in asset_ids:
            print("SKIP: integration tests need IT and FIN assets in the database")
            return

        it_viewer = next(a for a in accounts if a.department_code == "IT" and a.role == UserRole.VIEWER)
        fin_viewer = next(a for a in accounts if a.department_code == "FIN")
        admin = next(a for a in accounts if a.role == UserRole.ADMIN)

        # Login + first-login gate
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": it_viewer.email, "password": TEST_PASSWORD},
        )
        check("login succeeds", login_resp.status_code == 200)
        check(
            "login flags must_change_password",
            login_resp.json().get("must_change_password") is True,
        )

        viewer_headers = _auth_headers(client, it_viewer.email, TEST_PASSWORD)
        blocked = client.get("/api/v1/assets", headers=viewer_headers)
        check(
            "protected route blocked before password change",
            blocked.status_code == 403,
            blocked.text,
        )

        me_resp = client.get("/api/v1/auth/me", headers=viewer_headers)
        check("auth/me allowed before password change", me_resp.status_code == 200)

        change_resp = client.post(
            "/api/v1/auth/change-password",
            headers=viewer_headers,
            json={"current_password": TEST_PASSWORD, "new_password": NEW_PASSWORD},
        )
        check("change password succeeds", change_resp.status_code == 200)
        check(
            "must_change_password cleared",
            change_resp.json().get("must_change_password") is False,
        )

        active_headers = _auth_headers(client, it_viewer.email, NEW_PASSWORD)
        assets_resp = client.get(
            "/api/v1/assets?page_size=100&is_active=true", headers=active_headers
        )
        check("assets accessible after password change", assets_resp.status_code == 200)

        it_total = assets_resp.json()["total"]
        expected_it = dept_counts.get("IT", 0)
        check(
            "IT viewer asset count matches IT department",
            it_total == expected_it,
            f"got {it_total}, expected {expected_it}",
        )

        fin_headers = _auth_headers(client, fin_viewer.email, TEST_PASSWORD)
        client.post(
            "/api/v1/auth/change-password",
            headers=fin_headers,
            json={"current_password": TEST_PASSWORD, "new_password": NEW_PASSWORD},
        )
        fin_headers = _auth_headers(client, fin_viewer.email, NEW_PASSWORD)

        fin_blocked = client.get(f"/api/v1/assets/{asset_ids['IT']}", headers=fin_headers)
        check(
            "Finance viewer cannot access IT asset by id",
            fin_blocked.status_code == 403,
            fin_blocked.text,
        )

        fin_allowed = client.get(f"/api/v1/assets/{asset_ids['FIN']}", headers=fin_headers)
        check("Finance viewer can access Finance asset", fin_allowed.status_code == 200)

        write_blocked = client.post(
            "/api/v1/assets",
            headers=active_headers,
            json={
                "asset_tag": "TEST-AUTH-TAG",
                "name": "Should Fail",
                "asset_type_id": str(
                    db.execute(select(Asset.asset_type_id).limit(1)).scalar_one()
                ),
                "current_department_id": str(it_viewer.department_id),
                "current_status": "AVAILABLE",
            },
        )
        check("viewer cannot create assets", write_blocked.status_code == 403)

        admin_headers = _auth_headers(client, admin.email, TEST_PASSWORD)
        admin_assets = client.get(
            "/api/v1/assets?page_size=1&is_active=true", headers=admin_headers
        )
        check("admin can list assets org-wide", admin_assets.status_code == 200)
        admin_total = admin_assets.json()["total"]
        org_total = db.execute(
            select(func.count()).select_from(Asset).where(Asset.is_active.is_(True))
        ).scalar_one()
        check(
            "admin sees full org asset count",
            admin_total == org_total,
            f"got {admin_total}, expected {org_total}",
        )

        fin_total = client.get(
            "/api/v1/assets?page_size=1&is_active=true", headers=fin_headers
        ).json()["total"]
        check(
            "department viewers see fewer assets than admin",
            fin_total < admin_total and it_total < admin_total,
            f"IT={it_total}, FIN={fin_total}, admin={admin_total}",
        )

        workspace = client.get("/api/v1/dashboard/my-workspace", headers=active_headers)
        check("my-workspace endpoint works", workspace.status_code == 200)
        if workspace.status_code == 200:
            body = workspace.json()
            check("workspace includes department name", bool(body.get("department_name")))
            check("workspace includes assigned_assets list", "assigned_assets" in body)

        reset_resp = client.post(
            f"/api/v1/auth/users/{it_viewer.user_id}/reset-password",
            headers=admin_headers,
        )
        check("admin can reset user password", reset_resp.status_code == 200)
        temp_pw = reset_resp.json().get("temporary_password") if reset_resp.status_code == 200 else ""
        check("reset returns temporary password", bool(temp_pw))

        if temp_pw:
            relogin = client.post(
                "/api/v1/auth/login",
                json={"email": it_viewer.email, "password": temp_pw},
            )
            check(
                "user must change password after admin reset",
                relogin.json().get("must_change_password") is True,
            )

    except Exception as exc:
        check("integration suite", False, str(exc))
    finally:
        _cleanup_test_accounts(db)
        db.close()


def main() -> None:
    global passed, failed
    print("=== Auth & RBAC Tests ===")
    test_password_policy()
    test_access_scope()
    test_permissions_matrix()
    test_integration()

    print(f"\n=== Results: {passed} passed, {failed} failed ===")
    if failed:
        sys.exit(1)
    print("ALL AUTH/RBAC TESTS PASSED!")


if __name__ == "__main__":
    main()
