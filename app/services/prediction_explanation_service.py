from __future__ import annotations

from app.models.health_history import AssetHealthHistory
from app.schemas.explanation import ExplanationFactor, FactorSeverity, PredictionExplanation
from app.schemas.intelligence import RiskLevel
from app.services import narrative as narr
from ml.data.type_profiles import get_type_profile

_RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

_HIGH_MAINTENANCE_TYPES = {"Server", "Production Machine", "Networking Device", "UPS"}


class PredictionExplanationService:
    def build(
        self,
        *,
        features: dict,
        health_score: float,
        risk_level: RiskLevel | str,
        asset_name: str,
        previous_history: AssetHealthHistory | None = None,
        previous_risk_level: str | None = None,
    ) -> PredictionExplanation:
        risk_val = risk_level.value if hasattr(risk_level, "value") else str(risk_level)
        asset_type = str(features.get("asset_type", "Laptop"))
        factors: list[ExplanationFactor] = []
        anomaly_detected = False

        previous_health: float | None = None
        health_delta: float | None = None
        if previous_history and previous_history.health_score is not None:
            previous_health = float(previous_history.health_score)
            health_delta = health_score - previous_health
            if health_delta < -0.12:
                anomaly_detected = True
                factors.append(
                    ExplanationFactor(
                        factor="health_drop",
                        severity=FactorSeverity.HIGH,
                        message=narr.explanation_factor_message(
                            "health_drop",
                            value=f"{int(previous_health * 100)}% → {int(health_score * 100)}%",
                            severity="HIGH",
                        ),
                    )
                )

        if previous_risk_level and _RISK_ORDER.get(risk_val, 0) > _RISK_ORDER.get(previous_risk_level, 0):
            anomaly_detected = True
            factors.append(
                ExplanationFactor(
                    factor="risk_escalation",
                    severity=FactorSeverity.HIGH,
                    message=narr.explanation_factor_message(
                        "risk_escalation",
                        value=risk_val,
                        severity="HIGH",
                    ),
                )
            )

        failure_count = int(features.get("failure_count", 0))
        if failure_count >= 2:
            anomaly_detected = True
            severity = FactorSeverity.HIGH if failure_count >= 3 else FactorSeverity.MEDIUM
            factors.append(
                ExplanationFactor(
                    factor="failure_count",
                    severity=severity,
                    message=narr.explanation_factor_message(
                        "failure_count",
                        value=str(failure_count),
                        severity=severity.value,
                    ),
                )
            )

        days_since_maint = int(features.get("days_since_last_maintenance", 0))
        maint_threshold = 90 if asset_type in _HIGH_MAINTENANCE_TYPES else 180
        if days_since_maint > maint_threshold:
            anomaly_detected = True
            severity = FactorSeverity.HIGH if days_since_maint > maint_threshold * 1.5 else FactorSeverity.MEDIUM
            factors.append(
                ExplanationFactor(
                    factor="maintenance_overdue",
                    severity=severity,
                    message=narr.explanation_factor_message(
                        "maintenance_overdue",
                        value=str(days_since_maint),
                        severity=severity.value,
                    ),
                )
            )

        utilization = float(features.get("utilization_rate", 0))
        if utilization > 0.85:
            anomaly_detected = True
            factors.append(
                ExplanationFactor(
                    factor="high_utilization",
                    severity=FactorSeverity.MEDIUM,
                    message=narr.explanation_factor_message(
                        "high_utilization",
                        value=f"{int(utilization * 100)}%",
                        severity="MEDIUM",
                    ),
                )
            )

        downtime = float(features.get("downtime_hours", 0))
        profile = get_type_profile(asset_type)
        if downtime > profile.baseline_downtime_hours * 3:
            factors.append(
                ExplanationFactor(
                    factor="elevated_downtime",
                    severity=FactorSeverity.MEDIUM,
                    message=narr.explanation_factor_message(
                        "elevated_downtime",
                        value=f"{int(downtime)}h",
                        severity="MEDIUM",
                    ),
                )
            )

        age_days = int(features.get("asset_age_days", 0))
        if age_days > profile.expected_life_days * 0.85:
            factors.append(
                ExplanationFactor(
                    factor="asset_age",
                    severity=FactorSeverity.LOW,
                    message=narr.explanation_factor_message(
                        "asset_age",
                        value=str(age_days),
                        severity="LOW",
                    ),
                )
            )

        if health_score < 0.35 and not any(f.factor == "health_drop" for f in factors):
            factors.append(
                ExplanationFactor(
                    factor="critical_health",
                    severity=FactorSeverity.HIGH,
                    message=f"Predicted health is critically low at {int(health_score * 100)}%.",
                )
            )
            anomaly_detected = True

        severity_rank = {FactorSeverity.HIGH: 0, FactorSeverity.MEDIUM: 1, FactorSeverity.LOW: 2}
        factors.sort(key=lambda f: severity_rank.get(f.severity, 3))

        top_messages = [f.message for f in factors[:3]]
        health_pct = int(health_score * 100)
        band_key, band_label = narr.health_band_from_score(health_score)
        age_days = int(features.get("asset_age_days", 0))
        profile = get_type_profile(asset_type)

        brief_data = narr.enterprise_health_brief(
            asset_name=asset_name,
            asset_type=asset_type,
            health_pct=health_pct,
            health_band_label=band_label,
            risk_level=risk_val,
            factors=top_messages,
            days_since_maint=days_since_maint,
            failure_count=failure_count,
            health_delta=health_delta,
            age_days=age_days,
            expected_life_days=profile.expected_life_days,
        )
        from app.schemas.explanation import EnterpriseHealthBrief

        enterprise_brief = EnterpriseHealthBrief(**brief_data)
        summary = narr.enterprise_explanation_summary(
            asset_name=asset_name,
            health_pct=health_pct,
            health_band_label=band_label,
            is_improvement=bool(brief_data.get("is_improvement")),
        )

        return PredictionExplanation(
            anomaly_detected=anomaly_detected,
            health_delta=health_delta,
            previous_health_score=previous_health,
            factors=factors,
            summary=summary,
            enterprise_brief=enterprise_brief,
        )
