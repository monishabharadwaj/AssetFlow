import uuid

from app.core.access_scope import AccessContext
from app.core.enums import UserRole


def test_admin_is_org_wide() -> None:
    admin = AccessContext(
        user_id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        role=UserRole.ADMIN,
        department_id=uuid.uuid4(),
    )
    assert admin.is_org_wide
    assert admin.scoping_department_id() is None


def test_viewer_scoped_to_department() -> None:
    dept_a = uuid.uuid4()
    dept_b = uuid.uuid4()
    viewer = AccessContext(
        user_id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        role=UserRole.VIEWER,
        department_id=dept_a,
    )
    assert not viewer.is_org_wide
    assert viewer.scoping_department_id() == dept_a
    assert viewer.can_access_department(dept_a)
    assert not viewer.can_access_department(dept_b)
