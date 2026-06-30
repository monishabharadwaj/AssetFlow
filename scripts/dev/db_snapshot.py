"""Read-only snapshot of employees and login roles (no writes)."""
from sqlalchemy import create_engine, text

from app.core.config import settings

engine = create_engine(settings.database_url)
with engine.connect() as conn:
    emp_count = conn.execute(text("SELECT count(*) FROM employees")).scalar()
    user_count = conn.execute(text("SELECT count(*) FROM users")).scalar()
    asset_count = conn.execute(text("SELECT count(*) FROM assets")).scalar()
    print(f"Employees: {emp_count}  |  Login accounts: {user_count}  |  Assets: {asset_count}")

    print("\n--- ADMIN ---")
    for row in conn.execute(
        text(
            "SELECT e.first_name, e.last_name, e.email, e.job_title, d.code "
            "FROM users u JOIN employees e ON e.id = u.employee_id "
            "JOIN departments d ON d.id = e.department_id "
            "WHERE u.role = 'ADMIN'"
        )
    ):
        print(f"  {row[0]} {row[1]} | {row[2]} | {row[3]} | dept {row[4]}")

    print("\n--- Hannah Vargas ---")
    for row in conn.execute(
        text(
            "SELECT e.email, e.job_title, u.role, d.code "
            "FROM employees e "
            "LEFT JOIN users u ON u.employee_id = e.id "
            "LEFT JOIN departments d ON d.id = e.department_id "
            "WHERE lower(e.first_name) = 'hannah' AND lower(e.last_name) = 'vargas'"
        )
    ):
        print(f"  {row[0]} | {row[1]} | role={row[2]} | dept {row[3]}")

    print("\n--- Role counts ---")
    for row in conn.execute(
        text("SELECT role, count(*) FROM users GROUP BY role ORDER BY role")
    ):
        print(f"  {row[0]}: {row[1]}")
