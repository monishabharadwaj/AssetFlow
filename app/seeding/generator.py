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
from ml.config import DEFAULT_FEATURE_STATS, DEFAULT_MODEL_PATH
from ml.data.schema import risk_level_from_score
from ml.data.type_profiles import get_type_profile
from ml.etl.features import load_feature_stats, vectorize_row
from ml.predict import load_model

# Realistic enterprise health distribution, expressed as model-output bands.
_HEALTH_BANDS: list[tuple[str, float]] = [
    ("HEALTHY", 0.80),
    ("MONITOR", 0.12),
    ("WARNING", 0.05),
    ("CRITICAL", 0.03),
]

# Per-band feature ranges, calibrated so the FT-Transformer maps them into the
# intended health range: (age_days, days_since_maint, maint_count, failures, util).
_BAND_RANGES: dict[str, dict[str, tuple]] = {
    "HEALTHY": {"age": (30, 140), "days_since": (3, 12), "maint": (1, 1), "fail": (0, 0), "util": (0.15, 0.30)},
    "MONITOR": {"age": (250, 400), "days_since": (32, 58), "maint": (1, 1), "fail": (0, 0), "util": (0.40, 0.52)},
    "WARNING": {"age": (430, 510), "days_since": (90, 120), "maint": (1, 1), "fail": (0, 1), "util": (0.58, 0.68)},
    "CRITICAL": {"age": (530, 605), "days_since": (180, 340), "maint": (0, 0), "fail": (1, 1), "util": (0.80, 0.94)},
}

# Types that age more gracefully vs. those under harsher operational stress.
_DURABLE_TYPES = {"Office Furniture", "Monitor", "UPS"}
_HARSH_TYPES = {"Server", "Company Vehicle", "Delivery Van", "Production Machine"}


def _sample_band(rng: random.Random, type_name: str) -> str:
    weights = {name: w for name, w in _HEALTH_BANDS}
    if type_name in _DURABLE_TYPES:
        weights = {"HEALTHY": 0.92, "MONITOR": 0.06, "WARNING": 0.015, "CRITICAL": 0.005}
    elif type_name in _HARSH_TYPES:
        weights = {"HEALTHY": 0.70, "MONITOR": 0.18, "WARNING": 0.08, "CRITICAL": 0.04}
    names = list(weights.keys())
    return rng.choices(names, weights=[weights[n] for n in names], k=1)[0]


class _HealthScorer:
    """Loads the FT-Transformer once for fast batch scoring during seeding."""

    def __init__(self) -> None:
        self._ready = False
        try:
            self._model, self._checkpoint = load_model(DEFAULT_MODEL_PATH)
            self._stats = load_feature_stats(DEFAULT_FEATURE_STATS)
            self._ready = True
        except Exception:
            self._ready = False

    def score(self, features: dict) -> dict:
        if not self._ready:
            from ml.data.synthetic_generator import _compute_health_score

            score = _compute_health_score(random.Random(0), features)
            return {
                "health_score": round(score, 4),
                "risk_level": risk_level_from_score(score),
                "confidence": 0.6,
                "model_version": "causal_fallback",
                "training_dataset": "seed",
                "features_used": list(features.keys()),
            }
        import torch

        numeric, cat_idx = vectorize_row(features, self._stats)
        with torch.no_grad():
            pred = self._model(
                torch.tensor(numeric).unsqueeze(0),
                torch.tensor([cat_idx]),
            ).item()
        pred = max(0.0, min(1.0, pred))
        return {
            "health_score": round(pred, 4),
            "risk_level": risk_level_from_score(pred),
            "confidence": round(min(1.0, max(0.5, 1.0 - abs(pred - 0.5))), 4),
            "model_version": self._checkpoint.get("model_version", "ft_transformer_v1"),
            "training_dataset": self._checkpoint.get("training_dataset", "synthetic_v1_80k"),
            "features_used": list(features.keys()),
        }


def _build_band_features(rng: random.Random, type_name: str, band: str) -> dict:
    r = _BAND_RANGES[band]
    profile = get_type_profile(type_name)
    age = rng.randint(*r["age"])
    days_since = rng.randint(*r["days_since"])
    maint_count = rng.randint(*r["maint"])
    failures = rng.randint(*r["fail"])
    util = round(rng.uniform(*r["util"]), 3)
    op_hours = min(
        profile.max_operational_hours,
        profile.max_operational_hours * util * (age / profile.expected_life_days) * 2,
    )
    downtime = profile.baseline_downtime_hours * profile.downtime_sensitivity
    downtime += failures * 8.0 * profile.downtime_sensitivity
    return {
        "asset_type": type_name,
        "asset_age_days": age,
        "utilization_rate": util,
        "operational_hours": round(op_hours, 2),
        "maintenance_count": maint_count,
        "days_since_last_maintenance": days_since,
        "failure_count": failures,
        "downtime_hours": round(downtime, 2),
        "allocation_count": rng.randint(0, 3),
        "transfer_count": rng.randint(0, 2),
    }


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
                name=f"{dept.name} {type_name} #{num:04d}",
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

    # --- Per-asset lifecycle: maintenance history + current AI health assessment ---
    # Each active asset is assigned a realistic health band; features are generated
    # in-distribution so the FT-Transformer produces a believable fleet-wide spread.
    scorer = _HealthScorer()
    maint_descriptions = {
        MaintenanceType.PREVENTIVE: "Scheduled preventive service",
        MaintenanceType.CORRECTIVE: "Corrective repair",
        MaintenanceType.INSPECTION: "Routine inspection",
        MaintenanceType.UPGRADE: "Hardware/firmware upgrade",
        MaintenanceType.OTHER: "General service",
    }
    due_prob = {"HEALTHY": 0.04, "MONITOR": 0.12, "WARNING": 0.28, "CRITICAL": 0.45}

    for asset in [a for a in assets if a.is_active]:
        type_name = _type_name_from_asset(db, asset, type_by_name)
        band = _sample_band(rng, type_name)
        features = _build_band_features(rng, type_name, band)
        age = features["asset_age_days"]
        days_since = features["days_since_last_maintenance"]

        # Keep purchase date / warranty consistent with the sampled age.
        asset.purchase_date = date.today() - timedelta(days=age)
        warranty_years = rng.choice([3, 4, 5])
        asset.warranty_expiry = asset.purchase_date + timedelta(days=365 * warranty_years)
        if rng.random() < 0.08:
            asset.warranty_expiry = date.today() + timedelta(days=rng.randint(5, 28))

        # Completed maintenance history consistent with the band.
        for k in range(features["maintenance_count"]):
            offset = min(days_since + k * rng.randint(60, 140), age)
            sched = date.today() - timedelta(days=offset)
            mtype = rng.choices(
                [
                    MaintenanceType.PREVENTIVE,
                    MaintenanceType.CORRECTIVE,
                    MaintenanceType.INSPECTION,
                    MaintenanceType.UPGRADE,
                ],
                weights=[0.5, 0.2, 0.2, 0.1],
                k=1,
            )[0]
            maintenance.append(
                MaintenanceRecord(
                    asset_id=asset.id,
                    maintenance_type=mtype,
                    status=MaintenanceStatus.COMPLETED,
                    scheduled_date=sched,
                    completed_date=sched + timedelta(days=rng.randint(1, 7)),
                    cost=Decimal(str(rng.randint(50, 2500))),
                    description=f"{maint_descriptions[mtype]} for {asset.asset_tag}",
                    service_provider=rng.choice(["Internal IT", "VendorCare", "FleetServe"]),
                )
            )

        # Overdue / upcoming scheduled work, weighted toward worse-health bands.
        if rng.random() < due_prob[band]:
            mtype = (
                MaintenanceType.INSPECTION
                if band in ("WARNING", "CRITICAL")
                else MaintenanceType.PREVENTIVE
            )
            overdue = rng.random() < 0.6
            sched = (
                date.today() - timedelta(days=rng.randint(1, 30))
                if overdue
                else date.today() + timedelta(days=rng.randint(2, 21))
            )
            maintenance.append(
                MaintenanceRecord(
                    asset_id=asset.id,
                    maintenance_type=mtype,
                    status=rng.choice(
                        [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]
                    ),
                    scheduled_date=sched,
                    completed_date=None,
                    cost=None,
                    description=f"{maint_descriptions[mtype]} for {asset.asset_tag}",
                    service_provider=rng.choice(["Internal IT", "VendorCare", "FleetServe", None]),
                )
            )

        # Score the latest snapshot with the real model and persist it as the
        # current AI assessment (prediction_metadata is not None).
        result = scorer.score(features)
        health_score = result["health_score"]
        predicted_at = _utc(datetime.now(timezone.utc))
        depreciation = round(min(1.0, age / (365 * 7)), 4)
        prediction_metadata = {
            "model_version": result["model_version"],
            "predicted_at": predicted_at.isoformat(),
            "risk_level": result["risk_level"],
            "confidence": result["confidence"],
            "features_used": result["features_used"],
            "training_dataset": result["training_dataset"],
            "failure_count": features["failure_count"],
            "input_features": features,
        }
        health_rows.append(
            AssetHealthHistory(
                asset_id=asset.id,
                recorded_at=predicted_at,
                health_score=Decimal(str(round(health_score, 4))),
                condition_rating=max(1, min(10, int(health_score * 10))),
                operational_hours=Decimal(str(features["operational_hours"])),
                failure_count=features["failure_count"],
                days_since_last_maintenance=days_since,
                age_in_days=age,
                depreciation_ratio=Decimal(str(depreciation)),
                raw_features=features,
                prediction_metadata=prediction_metadata,
                notes="AI health assessment",
            )
        )

        # Short historical trend (older snapshots, slightly healthier, not AI-tagged).
        for j in range(1, rng.randint(2, 4) + 1):
            past = predicted_at - timedelta(days=j * rng.randint(25, 50))
            if past.date() <= asset.purchase_date:
                break
            past_score = max(0.05, min(0.99, health_score + rng.uniform(0.01, 0.05) * j))
            health_rows.append(
                AssetHealthHistory(
                    asset_id=asset.id,
                    recorded_at=past,
                    health_score=Decimal(str(round(past_score, 4))),
                    condition_rating=max(1, min(10, int(past_score * 10))),
                    operational_hours=Decimal(
                        str(round(features["operational_hours"] * (1 - 0.05 * j), 2))
                    ),
                    failure_count=max(0, features["failure_count"] - (1 if j > 1 else 0)),
                    days_since_last_maintenance=max(0, days_since - j * 20),
                    age_in_days=max(0, age - j * 35),
                    depreciation_ratio=Decimal(str(depreciation)),
                    raw_features=None,
                    notes=rng.choice(["Routine inspection", "Quarterly assessment"]),
                )
            )

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
