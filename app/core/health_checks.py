from __future__ import annotations

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


def check_database(db: Session) -> tuple[bool, str]:
    try:
        db.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as exc:
        return False, str(exc)


def check_ml_model() -> tuple[bool, str]:
    if not settings.ml_enabled:
        return True, "disabled"

    model_path = Path(settings.ml_model_path)
    if not model_path.is_file():
        return False, f"model not found: {model_path}"

    stats_path = Path(settings.ml_feature_stats_path)
    if not stats_path.is_file():
        return False, f"feature stats not found: {stats_path}"

    return True, "ready"


def readiness_report(db: Session) -> dict:
    db_ok, db_detail = check_database(db)
    ml_ok, ml_detail = check_ml_model()

    checks = {
        "database": {"ok": db_ok, "detail": db_detail},
        "ml_model": {"ok": ml_ok, "detail": ml_detail},
    }
    ready = db_ok and ml_ok
    return {
        "status": "ready" if ready else "degraded",
        "service": settings.app_name,
        "checks": checks,
    }
