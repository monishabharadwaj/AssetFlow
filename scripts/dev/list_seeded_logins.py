"""Remove synthetic demo login accounts and list seeded RBAC accounts."""
from sqlalchemy import create_engine, text

from app.core.config import settings

DEMO_EMAILS = ("admin@assetflow.app", "manager@assetflow.app", "viewer@assetflow.app")

engine = create_engine(settings.database_url)
with engine.begin() as conn:
    removed = conn.execute(
        text("DELETE FROM employees WHERE lower(email) = ANY(:emails)"),
        {"emails": list(DEMO_EMAILS)},
    ).rowcount
    print(f"Removed synthetic demo employees: {removed}")

with engine.connect() as conn:
    rows = conn.execute(
        text(
            "SELECT e.email, u.role FROM users u "
            "JOIN employees e ON e.id = u.employee_id "
            "ORDER BY u.role, e.email LIMIT 15"
        )
    ).fetchall()
    print("\nSeeded login accounts in your database:")
    for email, role in rows:
        print(f"  {role}: {email}")
    admin = conn.execute(
        text(
            "SELECT e.email FROM users u "
            "JOIN employees e ON e.id = u.employee_id WHERE u.role = 'ADMIN'"
        )
    ).fetchone()
    print(f"\nADMIN account: {admin[0] if admin else 'none'}")
