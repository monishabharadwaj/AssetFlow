from __future__ import annotations

from datetime import date

from app.core.enums import AllocationAction, MaintenanceStatus


def employee_display(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"


def allocation_headline(
    action: AllocationAction | str,
    *,
    asset_name: str,
    asset_tag: str,
    employee_name: str,
) -> str:
    action_val = action.value if hasattr(action, "value") else str(action)
    if action_val == AllocationAction.ASSIGN.value:
        return f"{asset_name} was assigned to {employee_name}"
    if action_val == AllocationAction.REASSIGN.value:
        return f"{asset_name} was reassigned to {employee_name}"
    if action_val == AllocationAction.RETURN.value:
        return f"{asset_name} was returned by {employee_name}"
    return f"{asset_name} allocation updated for {employee_name}"


def allocation_message(
    action: AllocationAction | str,
    *,
    asset_name: str,
    asset_tag: str,
    employee_name: str,
) -> str:
    headline = allocation_headline(
        action, asset_name=asset_name, asset_tag=asset_tag, employee_name=employee_name
    )
    return f"{headline} ({asset_tag})."


def transfer_message(
    *,
    asset_name: str,
    asset_tag: str,
    from_department: str,
    to_department: str,
    to_location: str,
) -> str:
    return (
        f"{asset_name} moved from {from_department} to {to_department} "
        f"({to_location})."
    )


def maintenance_activity_message(
    *,
    asset_name: str,
    asset_tag: str,
    status: MaintenanceStatus | str,
    maintenance_type: str,
) -> str:
    status_val = status.value if hasattr(status, "value") else str(status)
    if status_val == MaintenanceStatus.COMPLETED.value:
        return f"{asset_name} completed {maintenance_type.lower()} maintenance and returned to service."
    if status_val in (MaintenanceStatus.SCHEDULED.value, MaintenanceStatus.IN_PROGRESS.value):
        return f"{asset_name} has {status_val.replace('_', ' ').lower()} {maintenance_type.lower()} maintenance."
    return f"{asset_name} maintenance updated to {status_val.replace('_', ' ').lower()}."


def maintenance_attention_message(
    *,
    asset_name: str,
    scheduled_date,
) -> str:
    return f"{asset_name} has overdue maintenance scheduled for {scheduled_date}."


def in_maintenance_attention_message(*, asset_name: str, location: str) -> str:
    return f"{asset_name} is in maintenance at {location}."


def available_attention_message(*, asset_name: str, asset_tag: str) -> str:
    return f"{asset_name} ({asset_tag}) is available for assignment."


def health_snapshot_title(*, health_score: float | None) -> str:
    if health_score is not None and health_score < 0.5:
        return "Health snapshot recorded — condition needs review"
    return "Health snapshot recorded"


def health_snapshot_message(
    *,
    asset_name: str,
    health_score: float | None,
    condition_rating: int | None,
) -> str:
    if health_score is not None:
        pct = int(float(health_score) * 100)
        return f"{asset_name} health assessed at {pct}% with condition rating {condition_rating or 'N/A'}."
    return f"{asset_name} received a new health assessment."


def high_risk_attention_message(*, asset_name: str, score: float, risk_level: str) -> str:
    pct = int(float(score) * 100)
    return (
        f"{asset_name} AI health prediction is {pct}% ({risk_level} risk). "
        f"Review maintenance and operational history."
    )


# --- Assistant & recommendation narratives ---

_MAINTENANCE_TYPE_LABELS = {
    "PREVENTIVE": "preventive service",
    "CORRECTIVE": "repair",
    "UPGRADE": "upgrade",
    "INSPECTION": "inspection",
    "OTHER": "maintenance",
}


def maintenance_type_label(maintenance_type: str) -> str:
    key = maintenance_type.upper().replace(" ", "_")
    return _MAINTENANCE_TYPE_LABELS.get(key, maintenance_type.replace("_", " ").lower())


def scoring_required_message() -> str:
    return (
        "AI health scoring hasn't been run yet. "
        "Tap Run AI scoring on the Operations Center dashboard, then ask again."
    )


def assistant_capabilities_message() -> str:
    return format_assistant_reply(
        "I can help with:",
        [
            "Assets that need maintenance or are high risk",
            "Recent transfers and department ownership",
            "Fleet counts (assets, employees, laptops, and more)",
            "Finding assets by name, tag, or location",
        ],
        footer="Try a suggested prompt or ask in your own words.",
    )


def format_assistant_reply(
    intro: str | None,
    bullets: list[str],
    *,
    footer: str | None = None,
) -> str:
    lines: list[str] = []
    if intro:
        lines.append(intro)
    lines.extend(f"• {bullet}" for bullet in bullets)
    if footer:
        lines.append(footer)
    return "\n".join(lines)


def recommendation_card_title(
    asset_name: str,
    *,
    maintenance_type: str,
    urgent_health: bool = False,
) -> str:
    label = maintenance_type_label(maintenance_type)
    if urgent_health:
        return f"{asset_name} needs urgent service"
    if maintenance_type.upper() == "PREVENTIVE":
        return f"{asset_name} needs preventive service"
    return f"{asset_name} needs {label}"


def recommendation_rationale_health_risk(
    *,
    asset_name: str,
    asset_tag: str,
    health_pct: int,
    within_days: int = 7,
) -> str:
    return (
        f"Predicted health is only {health_pct}%. "
        f"Schedule preventive maintenance within {within_days} days ({asset_tag})."
    )


def recommendation_rationale_overdue(
    *,
    asset_name: str,
    asset_tag: str,
    maintenance_type: str,
    scheduled_date: date | None,
) -> str:
    label = maintenance_type_label(maintenance_type)
    date_text = scheduled_date.isoformat() if scheduled_date else "an earlier date"
    return f"{label.capitalize()} was due on {date_text}. Please schedule as soon as possible ({asset_tag})."


def recommendation_rationale_inspection(
    *,
    asset_name: str,
    asset_tag: str,
    within_days: int = 14,
) -> str:
    return (
        f"Moderate risk with repeated failures in its history. "
        f"Book an inspection within {within_days} days ({asset_tag})."
    )


def high_risk_bullet(*, asset_name: str, asset_tag: str, health_pct: int) -> str:
    return f"{asset_name} — health is critically low at {health_pct}% ({asset_tag})"


def maintenance_rec_bullet(
    *,
    asset_name: str,
    asset_tag: str,
    maintenance_type: str,
    detail: str,
) -> str:
    label = maintenance_type_label(maintenance_type)
    return f"{asset_name}: {detail} ({asset_tag})"


def transfer_bullet(*, headline: str, asset_tag: str) -> str:
    return f"{headline} ({asset_tag})"


def asset_list_bullet(*, asset_name: str, asset_tag: str, status: str) -> str:
    readable_status = status.replace("_", " ").lower()
    return f"{asset_name} — {readable_status} ({asset_tag})"


def dashboard_overview_narrative(
    *,
    total_active_assets: int,
    total_active_employees: int,
    maintenance_due_count: int,
    top_department: str | None,
    top_department_count: int | None,
) -> str:
    bullets = [
        f"{total_active_assets} active assets across the organization",
        f"{total_active_employees} active employees",
        f"{maintenance_due_count} assets with overdue maintenance",
    ]
    if top_department and top_department_count is not None:
        bullets.append(f"{top_department} has the most assets ({top_department_count})")
    return format_assistant_reply("Here's a quick snapshot of your fleet:", bullets)


def fleet_count_bullet(label: str, count: int) -> str:
    return f"{count} {label}"


def warranty_expiring_bullet(*, asset_name: str, asset_tag: str, expiry: date) -> str:
    return f"{asset_name} — warranty expires {expiry.isoformat()} ({asset_tag})"


def explanation_factor_message(factor: str, value: str, severity: str) -> str:
    templates = {
        "health_drop": f"Health score dropped significantly: {value}.",
        "risk_escalation": f"Risk level escalated to {value}.",
        "failure_count": f"High failure count detected: {value} failures.",
        "maintenance_overdue": f"Maintenance is overdue by {value} days.",
        "high_utilization": f"Asset utilization is very high: {value}.",
        "elevated_downtime": f"Asset experienced elevated downtime of {value}.",
        "asset_age": f"Asset age is high: {value} days.",
    }
    return templates.get(factor, f"Critical factor: {factor} ({value})")


def health_band_from_score(health_score: float) -> tuple[str, str]:
    pct = int(health_score * 100)
    if pct >= 90:
        return "EXCELLENT", "Excellent"
    if pct >= 75:
        return "HEALTHY", "Healthy"
    if pct >= 60:
        return "MONITOR", "Monitor"
    if pct >= 45:
        return "WARNING", "Warning"
    return "CRITICAL", "Critical"


def enterprise_health_brief(
    *,
    asset_name: str,
    asset_type: str,
    health_pct: int,
    health_band_label: str,
    risk_level: str,
    factors: list[str],
    days_since_maint: int,
    failure_count: int,
    health_delta: float | None,
    age_days: int,
    expected_life_days: int,
) -> dict:
    is_improvement = health_delta is not None and health_delta > 0
    confidence_label = "High Confidence" if risk_level in ("LOW", "HIGH") else "Moderate Confidence"
    
    remaining_days = expected_life_days - age_days
    if remaining_days <= 0:
        remaining_useful_life = "Expired (End of Life)"
    elif remaining_days < 30:
        remaining_useful_life = f"{remaining_days} days"
    elif remaining_days < 365:
        remaining_useful_life = f"{remaining_days // 30} months"
    else:
        remaining_useful_life = f"{remaining_days / 365:.1f} years"

    # Business impact mapping
    if risk_level == "HIGH":
        business_impact = f"Imminent failure risk for {asset_name}. Operation could be disrupted, causing downtime for users."
        recommended_action = "Schedule immediate servicing. Inspect hardware, check diagnostic logs, and replace worn-out components."
        estimated_downtime = "4 - 8 hours"
        estimated_effort = "High (Specialist required)"
        estimated_cost = "$250 - $500"
    elif risk_level == "MEDIUM":
        business_impact = f"Elevated warning state. Performance issues or intermittent faults may occur, leading to reduced productivity."
        recommended_action = "Schedule preventive check within 14 days. Review utilization metrics and check recent maintenance logs."
        estimated_downtime = "1 - 2 hours"
        estimated_effort = "Medium (Standard service)"
        estimated_cost = "$50 - $150"
    else:
        business_impact = "Normal operations. Asset is performing within baseline parameters with low probability of failure."
        recommended_action = "No immediate action required. Continue regular scheduling cycle and standard health scans."
        estimated_downtime = "None"
        estimated_effort = "Low (Routine inspection)"
        estimated_cost = "$0"

    what_happened = f"The {asset_name} is currently flagged as {health_band_label} with an overall health score of {health_pct}%."
    
    if factors:
        why_predicted = f"Assessment is driven by: {'; '.join(factors)}."
    else:
        why_predicted = "No critical anomalous factors detected. Health is within normal baseline parameters."

    return {
        "what_happened": what_happened,
        "why_predicted": why_predicted,
        "business_impact": business_impact,
        "recommended_action": recommended_action,
        "priority": risk_level,
        "estimated_downtime": estimated_downtime,
        "estimated_effort": estimated_effort,
        "estimated_cost": estimated_cost,
        "health_band": health_band_label,
        "confidence_label": confidence_label,
        "remaining_useful_life": remaining_useful_life,
        "is_improvement": is_improvement,
    }


def enterprise_explanation_summary(
    *,
    asset_name: str,
    health_pct: int,
    health_band_label: str,
    is_improvement: bool,
) -> str:
    direction = "improving" if is_improvement else "declining"
    return f"{asset_name} health score is {health_pct}% ({health_band_label} band), showing a {direction} trend."
