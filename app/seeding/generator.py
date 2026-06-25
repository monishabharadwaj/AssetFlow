from __future__ import annotations

import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import (
    AllocationAction,
    AssetStatus,
    MaintenanceStatus,
    MaintenanceType,
)
from app.models.allocation import AssetAllocation
from app.models.asset import Asset, AssetCategory, AssetType
from app.models.department import Department
from app.models.employee import Employee
from app.models.health_history import AssetHealthHistory
from app.models.maintenance import MaintenanceRecord
from app.models.transfer import AssetTransfer
from app.seeding.manifest import (
    ASSET_TYPE_SPECS,
    DEMO_ASSET_TAGS,
    DEPARTMENTS,
    DEPT_ASSET_WEIGHTS,
    DEPT_EMPLOYEE_WEIGHTS,
    EXTRA_ASSET_TYPES,
    FIRST_NAMES,
    LAST_NAMES,
    MANUFACTURERS,
)
from app.seeding.profiles import SeedProfile, history_start


def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _rand_date(rng: random.Random, start: date, end: date) -> date:
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=rng.randint(0, delta))


def _rand_datetime(rng: random.Random, start: date, end: date) -> datetime:
    d = _rand_date(rng, start, end)
    return _utc(datetime(d.year, d.month, d.day, rng.randint(8, 18), rng.randint(0, 59)))


def ensure_extra_asset_types(db: Session) -> dict[str, AssetType]:
    """Insert extra types from manifest; return name -> AssetType map for all types."""
    for category_name, types in EXTRA_ASSET_TYPES.items():
        category = db.execute(
            select(AssetCategory).where(AssetCategory.name == category_name)
        ).scalar_one()
        for type_name, description in types:
            existing = db.execute(
                select(AssetType).where(
                    AssetType.category_id == category.id,
                    AssetType.name == type_name,
                )
            ).scalar_one_or_none()
            if existing is None:
                db.add(
                    AssetType(
                        category_id=category.id,
                        name=type_name,
                        description=description,
                    )
                )
    db.flush()

    types = list(db.execute(select(AssetType)).scalars().all())
    return {t.name: t for t in types}


def seed_departments(db: Session, profile: SeedProfile) -> list[Department]:
    depts: list[Department] = []
    for code, name, description in DEPARTMENTS[: profile.departments]:
        depts.append(
            Department(code=code, name=name, description=description, is_active=True)
        )
    db.add_all(depts)
    db.flush()
    return depts


def seed_employees(
    db: Session,
    profile: SeedProfile,
    departments: list[Department],
    rng: random.Random,
) -> list[Employee]:
    dept_by_code = {d.code: d for d in departments}
    employees: list[Employee] = []
    used_emails: set[str] = set()
    idx = 1

    for code, weight in DEPT_EMPLOYEE_WEIGHTS.items():
        if code not in dept_by_code:
            continue
        count = max(1, int(profile.employees * weight))
        dept = dept_by_code[code]
        for _ in range(count):
            if len(employees) >= profile.employees:
                break
            first = rng.choice(FIRST_NAMES)
            last = rng.choice(LAST_NAMES)
            emp_code = f"{code}-{idx:04d}"
            email_base = f"{first.lower()}.{last.lower()}{idx}"
            email = f"{email_base}@assetflow.demo"
            while email in used_emails:
                idx += 1
                email = f"{first.lower()}.{last.lower()}{idx}@assetflow.demo"
            used_emails.add(email)
            employees.append(
                Employee(
                    department_id=dept.id,
                    employee_code=emp_code,
                    first_name=first,
                    last_name=last,
                    email=email,
                    job_title=rng.choice(
                        ["Analyst", "Engineer", "Manager", "Specialist", "Coordinator"]
                    ),
                    is_active=True,
                )
            )
            idx += 1

    while len(employees) < profile.employees:
        dept = rng.choice(departments)
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        emp_code = f"{dept.code}-{idx:04d}"
        email = f"{first.lower()}.{last.lower()}{idx}@assetflow.demo"
        employees.append(
            Employee(
                department_id=dept.id,
                employee_code=emp_code,
                first_name=first,
                last_name=last,
                email=email,
                job_title="Associate",
                is_active=True,
            )
        )
        idx += 1

    db.add_all(employees)
    db.flush()
    return employees


def _pick_department(rng: random.Random, departments: list[Department]) -> Department:
    codes = [d.code for d in departments]
    weights = [DEPT_ASSET_WEIGHTS.get(c, 0.05) for c in codes]
    total = sum(weights)
    weights = [w / total for w in weights]
    chosen = rng.choices(departments, weights=weights, k=1)[0]
    return chosen


def _tag_prefix(type_name: str, dept_code: str) -> str:
    mapping = {
        "Laptop": "LAP",
        "Desktop Workstation": "DSK",
        "Server": "SRV",
        "Networking Device": "NET",
        "Monitor": "MON",
        "Printer": "PRT",
        "Office Furniture": "FUR",
        "Conference AV": "AV",
        "UPS": "UPS",
        "Company Vehicle": "VEH",
        "Delivery Van": "VAN",
        "Production Machine": "MCH",
    }
    return f"{dept_code}-{mapping.get(type_name, 'AST')}"


def seed_assets(
    db: Session,
    profile: SeedProfile,
    departments: list[Department],
    employees: list[Employee],
    type_by_name: dict[str, AssetType],
    rng: random.Random,
    hist_start: date,
) -> list[Asset]:
    total = profile.active_assets + profile.inactive_assets
    type_names = [n for n in ASSET_TYPE_SPECS if n in type_by_name]
    weights = [ASSET_TYPE_SPECS[n][0] for n in type_names]
    employees_by_dept: dict[uuid.UUID, list[Employee]] = {}
    for emp in employees:
        employees_by_dept.setdefault(emp.department_id, []).append(emp)

    assets: list[Asset] = []
    tag_counters: dict[str, int] = {}

    # Reserve fixed demo tags first
    demo_specs = [
        (DEMO_ASSET_TAGS["laptop"], "Laptop", "ENG", "Engineering Laptop 0001", True),
        (DEMO_ASSET_TAGS["vehicle"], "Delivery Van", "OPS", "Operations Van 001", True),
        (DEMO_ASSET_TAGS["server"], "Server", "IT", "Production Server 01", False),
        (DEMO_ASSET_TAGS["printer"], "Printer", "ADM", "Admin Printer 001", False),
    ]
    dept_by_code = {d.code: d for d in departments}

    for tag, type_name, dept_code, name, assignable in demo_specs:
        if dept_code not in dept_by_code or type_name not in type_by_name:
            continue
        dept = dept_by_code[dept_code]
        purchase = hist_start + timedelta(days=rng.randint(30, 120))
        asset = Asset(
            asset_tag=tag,
            name=name,
            asset_type_id=type_by_name[type_name].id,
            purchase_date=purchase,
            purchase_cost=Decimal(str(rng.randint(500, 8000))),
            current_status=AssetStatus.AVAILABLE,
            current_location=_location(rng, type_name, dept.code, 1),
            current_department_id=dept.id,
            serial_number=f"SN-{tag}",
            manufacturer=rng.choice(MANUFACTURERS.get(type_name, ["Generic"])),
            model=f"Model-{tag[-3:]}",
            warranty_expiry=purchase + timedelta(days=365 * 3),
            is_active=True,
        )
        assets.append(asset)
        tag_counters[_tag_prefix(type_name, dept_code)] = 1

    while len(assets) < total:
        type_name = rng.choices(type_names, weights=weights, k=1)[0]
        dept = _pick_department(rng, departments)
        prefix = _tag_prefix(type_name, dept.code)
        tag_counters[prefix] = tag_counters.get(prefix, 0) + 1
        num = tag_counters[prefix]
        tag = f"{prefix}-{num:04d}"
        if any(a.asset_tag == tag for a in assets):
            continue
        purchase = _rand_date(rng, hist_start, date.today() - timedelta(days=30))
        assets.append(
            Asset(
                asset_tag=tag,
                name=f"{type_name} {dept.code}-{num:04d}",
                asset_type_id=type_by_name[type_name].id,
                purchase_date=purchase,
                purchase_cost=Decimal(str(rng.randint(200, 12000))),
                current_status=AssetStatus.AVAILABLE,
                current_location=_location(rng, type_name, dept.code, num),
                current_department_id=dept.id,
                serial_number=f"SN-{uuid.uuid4().hex[:8].upper()}",
                manufacturer=rng.choice(MANUFACTURERS.get(type_name, ["Generic"])),
                model=f"{type_name[:3].upper()}-{num}",
                warranty_expiry=purchase + timedelta(days=365 * rng.randint(1, 5)),
                is_active=True,
            )
        )

    demo_tags = set(DEMO_ASSET_TAGS.values())
    eligible_inactive = [a for a in assets if a.asset_tag not in demo_tags]
    inactive_count = profile.inactive_assets
    for asset in eligible_inactive[-inactive_count:]:
        asset.is_active = False
        asset.current_status = rng.choice([AssetStatus.RETIRED, AssetStatus.DISPOSED])

    # Assign final statuses for active assets
    active_assets = [a for a in assets if a.is_active]
    rng.shuffle(active_assets)
    n = len(active_assets)
    assigned_n = int(n * 0.50)
    maintenance_n = int(n * 0.07)

    for asset in active_assets[:assigned_n]:
        type_name = _resolve_type_name(db, asset, type_by_name)
        assignable = ASSET_TYPE_SPECS.get(type_name, (0, False, ""))[1]
        if assignable:
            dept_emps = employees_by_dept.get(asset.current_department_id, employees)
            emp = rng.choice(dept_emps)
            asset.current_status = AssetStatus.ASSIGNED
            asset.current_assigned_employee_id = emp.id
        else:
            asset.current_status = AssetStatus.AVAILABLE

    for asset in active_assets[assigned_n : assigned_n + maintenance_n]:
        asset.current_status = AssetStatus.IN_MAINTENANCE
        asset.current_assigned_employee_id = None

    for asset in active_assets[assigned_n + maintenance_n :]:
        asset.current_status = AssetStatus.AVAILABLE
        asset.current_assigned_employee_id = None

    db.add_all(assets)
    db.flush()
    return assets


def _resolve_type_name(
    db: Session, asset: Asset, type_by_name: dict[str, AssetType]
) -> str:
    for name, t in type_by_name.items():
        if t.id == asset.asset_type_id:
            return name
    t = db.get(AssetType, asset.asset_type_id)
    return t.name if t else "Laptop"


def _location(rng: random.Random, type_name: str, dept_code: str, num: int) -> str:
    _, _, prefix = ASSET_TYPE_SPECS.get(type_name, (0, False, "Office"))
    if "Data Center" in prefix or "Server" in type_name:
        return f"{prefix} Rack {chr(65 + num % 5)}{num % 20}"
    if "Fleet" in prefix or "Vehicle" in type_name or "Van" in type_name:
        return f"{prefix} Bay {num % 12 + 1}"
    if "Network" in prefix:
        return f"{dept_code} Network Closet {num % 5 + 1}"
    return f"{prefix} — Desk {num % 80 + 1}"


def seed_history(
    db: Session,
    profile: SeedProfile,
    departments: list[Department],
    employees: list[Employee],
    assets: list[Asset],
    type_by_name: dict[str, AssetType],
    rng: random.Random,
    hist_start: date,
) -> dict[str, int]:
    hist_end = date.today()
    allocations: list[AssetAllocation] = []
    transfers: list[AssetTransfer] = []
    maintenance: list[MaintenanceRecord] = []
    health_rows: list[AssetHealthHistory] = []

    employees_by_dept: dict[uuid.UUID, list[Employee]] = {}
    for emp in employees:
        employees_by_dept.setdefault(emp.department_id, []).append(emp)

    assignable_assets = [
        a
        for a in assets
        if a.is_active
        and ASSET_TYPE_SPECS.get(_type_name_from_asset(db, a, type_by_name), (0, False, ""))[1]
    ]

    # Historical allocations
    for _ in range(profile.allocation_events):
        asset = rng.choice(assignable_assets)
        emp = rng.choice(employees_by_dept.get(asset.current_department_id, employees))
        action = rng.choices(
            [AllocationAction.ASSIGN, AllocationAction.REASSIGN, AllocationAction.RETURN],
            weights=[0.45, 0.30, 0.25],
            k=1,
        )[0]
        at = _rand_datetime(rng, hist_start, hist_end)
        returned = None
        if action == AllocationAction.RETURN:
            returned = at + timedelta(days=rng.randint(30, 400))
        allocations.append(
            AssetAllocation(
                asset_id=asset.id,
                employee_id=emp.id,
                action=action,
                allocated_at=at,
                returned_at=returned,
                notes=rng.choice([None, "Routine assignment", "Role change", "Project allocation"]),
            )
        )

    # Current assignment record for ASSIGNED assets
    for asset in assets:
        if asset.current_status != AssetStatus.ASSIGNED or not asset.current_assigned_employee_id:
            continue
        allocations.append(
            AssetAllocation(
                asset_id=asset.id,
                employee_id=asset.current_assigned_employee_id,
                action=AllocationAction.ASSIGN,
                allocated_at=_utc(datetime.now(timezone.utc) - timedelta(days=rng.randint(1, 90))),
                notes="Current assignment",
            )
        )

    # Transfers
    for _ in range(profile.transfer_events):
        asset = rng.choice([a for a in assets if a.is_active])
        from_dept_id = asset.current_department_id
        to_dept = rng.choice([d for d in departments if d.id != from_dept_id])
        at = _rand_datetime(rng, hist_start, hist_end)
        transfers.append(
            AssetTransfer(
                asset_id=asset.id,
                from_department_id=from_dept_id,
                to_department_id=to_dept.id,
                from_location=asset.current_location,
                to_location=_location(rng, _type_name_from_asset(db, asset, type_by_name), to_dept.code, rng.randint(1, 50)),
                transferred_at=at,
                reason=rng.choice(
                    [None, "Department reorganization", "Employee relocation", "Fleet redeployment"]
                ),
            )
        )

    # Maintenance
    maint_types = list(MaintenanceType)
    overdue_target = max(15, profile.maintenance_records // 10)
    overdue_created = 0

    for i in range(profile.maintenance_records):
        asset = rng.choice([a for a in assets if a.is_active])
        mtype = rng.choice(maint_types)
        if overdue_created < overdue_target and rng.random() < 0.25:
            status = rng.choice([MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS])
            scheduled = date.today() - timedelta(days=rng.randint(1, 45))
            overdue_created += 1
        else:
            status = rng.choices(
                [MaintenanceStatus.COMPLETED, MaintenanceStatus.SCHEDULED, MaintenanceStatus.CANCELLED],
                weights=[0.55, 0.30, 0.15],
                k=1,
            )[0]
            scheduled = _rand_date(rng, hist_start, hist_end)
        completed = None
        if status == MaintenanceStatus.COMPLETED:
            completed = scheduled + timedelta(days=rng.randint(1, 14)) if scheduled else None
        maintenance.append(
            MaintenanceRecord(
                asset_id=asset.id,
                maintenance_type=mtype,
                status=status,
                scheduled_date=scheduled,
                completed_date=completed,
                cost=Decimal(str(rng.randint(50, 2500))) if status == MaintenanceStatus.COMPLETED else None,
                description=f"{mtype.value.title()} maintenance for {asset.asset_tag}",
                service_provider=rng.choice(["Internal IT", "VendorCare", "FleetServe", None]),
            )
        )

    # Health snapshots
    high_touch = {"Laptop", "Desktop Workstation", "Server", "Company Vehicle", "Delivery Van", "Production Machine"}
    created = 0

    for asset in assets:
        if not asset.is_active or created >= profile.health_snapshots:
            break
        type_name = _type_name_from_asset(db, asset, type_by_name)
        count = max(1, profile.health_snapshots // max(len([a for a in assets if a.is_active]), 1))
        if type_name in high_touch:
            count += 4
        if type_name in ("Office Furniture", "Conference AV"):
            count = max(1, count // 4)
        age_days = (date.today() - asset.purchase_date).days
        for _ in range(count):
            if created >= profile.health_snapshots:
                break
            recorded = _rand_datetime(
                rng,
                max(hist_start, asset.purchase_date),
                hist_end,
            )
            degradation = min(1.0, age_days / (365 * 5))
            base_score = 0.95 - degradation * 0.4 - rng.uniform(0, 0.15)
            health_score = max(0.1, min(1.0, base_score))
            failure_count = rng.randint(0, 3) if degradation > 0.3 else rng.randint(0, 1)
            days_since_maint = rng.randint(0, 180)
            raw_features = {
                "operational_hours": round(rng.uniform(100, 8000), 2),
                "failure_count": failure_count,
                "days_since_last_maintenance": days_since_maint,
                "age_in_days": age_days,
                "depreciation_ratio": round(min(1.0, age_days / (365 * 7)), 4),
            }
            health_rows.append(
                AssetHealthHistory(
                    asset_id=asset.id,
                    recorded_at=recorded,
                    health_score=Decimal(str(round(health_score, 4))),
                    condition_rating=max(1, min(10, int(health_score * 10))),
                    operational_hours=Decimal(str(raw_features["operational_hours"])),
                    failure_count=failure_count,
                    days_since_last_maintenance=days_since_maint,
                    age_in_days=age_days,
                    depreciation_ratio=Decimal(str(raw_features["depreciation_ratio"])),
                    raw_features=raw_features,
                    notes=rng.choice([None, "Routine inspection", "Quarterly assessment"]),
                )
            )
            created += 1

    db.add_all(allocations)
    db.add_all(transfers)
    db.add_all(maintenance)
    db.add_all(health_rows)
    db.commit()

    return {
        "departments": len(departments),
        "employees": len(employees),
        "assets": len(assets),
        "allocations": len(allocations),
        "transfers": len(transfers),
        "maintenance": len(maintenance),
        "health_snapshots": len(health_rows),
    }


def _type_name_from_asset(db: Session, asset: Asset, type_by_name: dict[str, AssetType]) -> str:
    for name, t in type_by_name.items():
        if t.id == asset.asset_type_id:
            return name
    t = db.get(AssetType, asset.asset_type_id)
    return t.name if t else "Laptop"


def run_seed(db: Session, profile: SeedProfile, *, reset: bool = False) -> dict[str, int]:
    from app.seeding.reset import reset_operational_data

    if reset:
        reset_operational_data(db)

    rng = random.Random(profile.random_seed)
    hist_start = history_start(months=profile.history_months)

    type_by_name = ensure_extra_asset_types(db)
    departments = seed_departments(db, profile)
    employees = seed_employees(db, profile, departments, rng)
    assets = seed_assets(db, profile, departments, employees, type_by_name, rng, hist_start)
    counts = seed_history(
        db, profile, departments, employees, assets, type_by_name, rng, hist_start
    )
    counts["profile"] = profile.name
    return counts
