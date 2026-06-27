from __future__ import annotations

from datetime import date

from app.core.enums import AllocationAction, MaintenanceStatus


def employee_display(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"


def asset_context_phrase(
    *,
    asset_type: str | None = None,
    department_name: str | None = None,
) -> str:
    """Plain-language fleet context for recommendations and alerts."""
    if asset_type and department_name:
        return f"{asset_type} assigned to {department_name}"
    if asset_type:
        return asset_type
    if department_name:
        return f"Asset in {department_name}"
    return "This asset"


def recommendation_card_title(
    asset_tag: str,
    *,
    maintenance_type: str,
    urgent_health: bool = False,
) -> str:
    label = maintenance_type_label(maintenance_type)
    if urgent_health:
        return f"{asset_tag} needs urgent maintenance"
    if maintenance_type.upper() == "PREVENTIVE":
        return f"{asset_tag} needs preventive maintenance"
    return f"{asset_tag} needs {label}"


def recommendation_rationale_health_risk(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    health_pct: int,
    within_days: int = 7,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    return (
        f"{context}: predicted health is {health_pct}% (high risk). "
        f"Schedule preventive maintenance within {within_days} days."
    )


def recommendation_rationale_overdue(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    maintenance_type: str,
    scheduled_date: date | None,
) -> str:
    label = maintenance_type_label(maintenance_type)
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    date_text = scheduled_date.isoformat() if scheduled_date else "an earlier date"
    return (
        f"{context} ({asset_tag}): {label.lower()} was due on {date_text}. "
        "Please schedule as soon as possible."
    )


def recommendation_rationale_inspection(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    within_days: int = 14,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    return (
        f"{context} ({asset_tag}): moderate risk with repeated failures in its history. "
        f"Book an inspection within {within_days} days."
    )


def high_risk_bullet(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    health_pct: int,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    return f"{asset_tag} — {context}: health is critically low at {health_pct}%"


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


def high_risk_attention_message(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    score: float,
    risk_level: str,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    pct = int(float(score) * 100)
    return (
        f"{asset_tag} ({context}): AI health is {pct}% ({risk_level} risk). "
        f"Review maintenance and operational history."
    )


# --- Assistant & recommendation narratives ---

_MAINTENANCE_TYPE_LABELS = {
    "PREVENTIVE": "preventive service",
    "CORRECTIVE": "repair",
    "UPGRADE": "upgrade",
    "INSPECTION": "inspection",
    "OTHER": "maintenance",
    "REPLACEMENT": "replacement",
    "WARRANTY_RENEWAL": "warranty renewal",
    "MONITORING": "monitoring",
}


def recommendation_rationale_replacement(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    health_pct: int,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    return (
        f"{context} ({asset_tag}): health has fallen to {health_pct}% and the asset is near "
        "end-of-life. Evaluate replacement rather than further repair."
    )


def recommendation_rationale_warranty(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    expiry: date | None,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    when = expiry.isoformat() if expiry else "soon"
    return (
        f"{context} ({asset_tag}): warranty expires {when}. "
        "Renew or extend coverage before it lapses."
    )


def recommendation_rationale_upgrade(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    return (
        f"{context} ({asset_tag}): heavily utilized and aging while still healthy. "
        "Plan a performance upgrade to extend useful life."
    )


def recommendation_rationale_monitoring(
    *,
    asset_tag: str,
    asset_type: str | None,
    department_name: str | None,
    health_pct: int,
) -> str:
    context = asset_context_phrase(asset_type=asset_type, department_name=department_name)
    return (
        f"{context} ({asset_tag}): health is {health_pct}% (monitor range). "
        "No action needed yet — keep an eye on the next assessment."
    )


def recommendation_card_title_category(asset_tag: str, *, category: str) -> str:
    titles = {
        "REPLACEMENT": f"{asset_tag} — plan replacement",
        "WARRANTY_RENEWAL": f"{asset_tag} — renew warranty",
        "UPGRADE": f"{asset_tag} — schedule upgrade",
        "MONITORING": f"{asset_tag} — keep monitoring",
        "INSPECTION": f"{asset_tag} needs inspection",
        "PREVENTIVE": f"{asset_tag} needs preventive maintenance",
    }
    return titles.get(category, f"{asset_tag} needs {maintenance_type_label(category)}")


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
            "High-risk and healthy assets (AI health scores)",
            "Health details for a specific asset tag (e.g. IT-LAP-0001)",
            "Overdue maintenance and assets currently in maintenance",
            "AI maintenance recommendations and warranty renewals",
            "Recent transfers, assignments, and completed maintenance",
            "Assets in a department or assigned to an employee",
            "Fleet counts (assets, employees, laptops, and more)",
            "Finding assets by name, tag, status, or location",
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


def department_summary_bullet(
    *,
    department_name: str,
    asset_count: int,
    employee_count: int,
) -> str:
    return f"{department_name}: {asset_count} active assets, {employee_count} employees"


def employee_assets_intro(*, employee_name: str, asset_count: int) -> str:
    if asset_count == 0:
        return f"{employee_name} has no assets currently assigned."
    return f"{employee_name} has {asset_count} assigned asset{'s' if asset_count != 1 else ''}:"


def overdue_maintenance_bullet(
    *,
    asset_tag: str,
    maintenance_type: str,
    scheduled_date: date | None,
) -> str:
    when = scheduled_date.isoformat() if scheduled_date else "unknown date"
    label = maintenance_type_label(maintenance_type)
    return f"{asset_tag} — overdue {label} (scheduled {when})"


def allocation_activity_bullet(
    *,
    asset_tag: str,
    employee_name: str,
    action: str,
) -> str:
    verb = action.replace("_", " ").lower()
    return f"{asset_tag} {verb} to {employee_name}"


def asset_health_summary_bullet(
    *,
    asset_tag: str,
    health_pct: int,
    risk_level: str,
    band_label: str,
) -> str:
    return f"{asset_tag} — {band_label} at {health_pct}% ({risk_level} risk)"


def health_trend_bullet(*, recorded_at: str, health_pct: int) -> str:
    return f"{recorded_at}: {health_pct}%"


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


def weekly_ops_brief_summary(
    *,
    total_assets: int,
    high_risk_count: int,
    maintenance_due: int,
    drift_count: int,
) -> str:
    return (
        f"This week the fleet has {total_assets} active assets under management. "
        f"AI scoring flagged {high_risk_count} high-risk "
        f"asset{'s' if high_risk_count != 1 else ''}, "
        f"{maintenance_due} item{'s' if maintenance_due != 1 else ''} overdue for maintenance, "
        f"and {drift_count} asset{'s' if drift_count != 1 else ''} showing a significant health decline. "
        "Prioritize the high-risk and overdue items to keep operations stable."
    )


def policy_auto_maintenance_message(
    *,
    asset_name: str,
    maintenance_type: str,
    scheduled_date: date,
) -> str:
    label = maintenance_type_label(maintenance_type)
    return (
        f"{asset_name} was automatically scheduled for {label} on "
        f"{scheduled_date.isoformat()} based on its AI health risk."
    )


def enterprise_explanation_summary(
    *,
    asset_name: str,
    health_pct: int,
    health_band_label: str,
    is_improvement: bool,
) -> str:
    direction = "improving" if is_improvement else "declining"
    return f"{asset_name} health score is {health_pct}% ({health_band_label} band), showing a {direction} trend."
