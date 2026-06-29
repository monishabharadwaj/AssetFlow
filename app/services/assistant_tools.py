from __future__ import annotations

import re
import uuid
from datetime import date

from app.core.enums import AssetStatus
from app.repositories.asset_repository import AssetRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.health_history_repository import HealthHistoryRepository
from app.services import narrative as narr
from app.services.assistant_parsing import (
    department_ranking_mode,
    extract_asset_tag,
    extract_department_query,
    extract_employee_query,
    extract_status_query,
)
from app.services.assistant_intents import extract_search_term, extract_type_and_department
from app.services.asset_service import AssetService
from app.services.dashboard_service import DashboardService
from app.services.prediction_service import PredictionService
from app.services.recommendation_service import RecommendationService

_ASSET_TYPE_ALIASES: dict[str, str] = {
    "laptop": "Laptop",
    "laptops": "Laptop",
    "desktop": "Desktop Workstation",
    "desktops": "Desktop Workstation",
    "server": "Server",
    "servers": "Server",
    "printer": "Printer",
    "printers": "Printer",
    "monitor": "Monitor",
    "monitors": "Monitor",
    "van": "Delivery Van",
    "vans": "Delivery Van",
    "vehicle": "Company Vehicle",
    "vehicles": "Company Vehicle",
}


class AssistantTools:
    def __init__(
        self,
        dashboard_service: DashboardService,
        asset_service: AssetService,
        prediction_service: PredictionService,
        recommendation_service: RecommendationService,
        dashboard_repository: DashboardRepository,
        asset_repository: AssetRepository,
        department_repository: DepartmentRepository,
        employee_repository: EmployeeRepository,
        health_history_repository: HealthHistoryRepository,
    ) -> None:
        self.dashboard = dashboard_service
        self.assets = asset_service
        self.predictions = prediction_service
        self.recommendations = recommendation_service
        self.dashboard_repo = dashboard_repository
        self.asset_repo = asset_repository
        self.department_repo = department_repository
        self.employee_repo = employee_repository
        self.health_repo = health_history_repository

    @staticmethod
    def _result(
        *,
        data_text: str,
        fallback_answer: str,
        sources: list[dict] | None = None,
        cache_required: bool = False,
        skip_ollama: bool = False,
        ollama_validation: str = "relaxed",
    ) -> dict:
        payload: dict = {
            "data_text": data_text,
            "fallback_answer": fallback_answer,
            "sources": sources or [],
            "ollama_validation": ollama_validation,
        }
        if cache_required:
            payload["cache_required"] = True
        if skip_ollama:
            payload["skip_ollama"] = True
        return payload

    def _scoring_required(self) -> dict:
        return self._result(
            data_text="Prediction cache is empty.",
            fallback_answer=narr.scoring_required_message(),
            cache_required=True,
        )

    def _asset_sources(self, assets) -> list[dict]:
        return [
            {"label": a.asset_tag, "asset_id": str(a.id), "url": f"/assets/{a.id}"}
            for a in assets
        ]

    def get_dashboard_summary(self) -> dict:
        total_active_assets = self.dashboard_repo.count_assets(active_only=True)
        total_active_employees = self.dashboard_repo.count_employees(active_only=True)
        maintenance_due_count = self.dashboard_repo.maintenance_due_count()
        dept_rows = self.dashboard_repo.assets_by_department()
        top_dept = dept_rows[0] if dept_rows else None
        fallback = narr.dashboard_overview_narrative(
            total_active_assets=total_active_assets,
            total_active_employees=total_active_employees,
            maintenance_due_count=maintenance_due_count,
            top_department=top_dept[1] if top_dept else None,
            top_department_count=top_dept[2] if top_dept else None,
        )
        dept_lines = [f"{name}: {count}" for _, name, count in dept_rows[:5]]
        data_text = (
            f"Total assets: {total_active_assets}. "
            f"Employees: {total_active_employees}. "
            f"Maintenance due: {maintenance_due_count}. "
            f"Top departments: {'; '.join(dept_lines)}."
        )
        return self._result(
            data_text=data_text,
            fallback_answer=fallback,
        )

    def get_department_ranking(self, message: str) -> dict:
        dept_rows = self.dashboard_repo.assets_by_department()
        if not dept_rows:
            return self._result(
                data_text="No departments with active assets.",
                fallback_answer=narr.format_assistant_reply(
                    "I couldn't find any departments with active assets.",
                    [],
                ),
            )

        mode = department_ranking_mode(message)
        if mode == "fewest":
            _, name, count = min(dept_rows, key=lambda row: (row[2], row[1]))
        else:
            _, name, count = dept_rows[0]

        answer = narr.department_ranking_answer(
            department_name=name,
            asset_count=count,
            ranking=mode,
        )
        return self._result(
            data_text=f"{name}: {count} active assets (ranking={mode})",
            fallback_answer=answer,
            ollama_validation="minimal",
        )

    def get_department_maintenance_ranking(self) -> dict:
        rows = self.dashboard_repo.open_maintenance_by_department()
        if not rows:
            return self._result(
                data_text="No open maintenance records by department.",
                fallback_answer=narr.format_assistant_reply(
                    "No departments have open maintenance records right now.",
                    [],
                ),
            )
        _, name, count = rows[0]
        answer = narr.department_maintenance_ranking_answer(
            department_name=name,
            maintenance_count=count,
        )
        return self._result(
            data_text=f"{name}: {count} open maintenance records",
            fallback_answer=answer,
            ollama_validation="minimal",
        )

    def get_maintenance_this_week(self) -> dict:
        rows = self.dashboard_repo.maintenance_scheduled_this_week(limit=8)
        if not rows:
            return self._result(
                data_text="No maintenance scheduled this week.",
                fallback_answer=narr.format_assistant_reply(
                    "No assets have maintenance scheduled for the next 7 days.",
                    [],
                ),
            )
        bullets = [
            narr.overdue_maintenance_bullet(
                asset_tag=asset.asset_tag,
                maintenance_type=record.maintenance_type.value,
                scheduled_date=record.scheduled_date,
            )
            for record, asset in rows
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"{len(bullets)} asset{'s' if len(bullets) != 1 else ''} with maintenance due this week:",
                bullets,
            ),
            sources=self._asset_sources([asset for _, asset in rows]),
        )

    def get_warranty_this_month(self) -> dict:
        assets = self.dashboard_repo.warranty_expiring_this_month(limit=8)
        if not assets:
            return self._result(
                data_text="No warranties expiring this month.",
                fallback_answer=narr.format_assistant_reply(
                    "No warranties are expiring this calendar month.",
                    [],
                ),
            )
        bullets = [
            narr.warranty_expiring_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                expiry=a.warranty_expiry,  # type: ignore[arg-type]
            )
            for a in assets
            if a.warranty_expiry
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                "Warranties expiring this month:",
                bullets,
            ),
            sources=self._asset_sources(assets),
        )

    def get_assets_by_department_and_type(self, message: str) -> dict:
        type_name, dept_query = extract_type_and_department(message)
        if not type_name or not dept_query:
            return self._result(
                data_text="No department and asset type detected.",
                fallback_answer=narr.format_assistant_reply(
                    "Tell me both a department and asset type.",
                    ["Example: Which laptops belong to Engineering?"],
                ),
            )
        department = self.department_repo.find_best_match(dept_query)
        if not department:
            return self._result(
                data_text=f"No department matched '{dept_query}'.",
                fallback_answer=narr.format_assistant_reply(
                    f"I couldn't find a department matching '{dept_query}'.",
                    [],
                ),
            )
        assets, total = self.asset_repo.search_by_type_and_department(
            type_name=type_name,
            department_id=department.id,
            page=1,
            page_size=8,
        )
        intro = narr.dept_type_assets_intro(
            department_name=department.name,
            type_name=type_name,
            total=total,
        )
        if not assets:
            return self._result(data_text=intro, fallback_answer=intro)
        bullets = [
            narr.asset_list_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                status=a.current_status.value,
            )
            for a in assets
        ]
        return self._result(
            data_text=f"{intro} " + "; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(intro, bullets),
            sources=self._asset_sources(assets),
        )

    def get_high_risk_by_type(self, message: str) -> dict:
        if not self.predictions.is_cache_warm():
            return self._scoring_required()

        from app.services.assistant_intents import extract_asset_type_query

        type_name = extract_asset_type_query(message)
        if not type_name:
            return self.get_high_risk_assets()

        high_risk = self.predictions.get_high_risk(limit=20)
        filtered = [
            item
            for item in high_risk.items
            if item.asset_type_name and type_name.lower() in item.asset_type_name.lower()
        ]
        if not filtered:
            return self._result(
                data_text=f"No high-risk {type_name.lower()}s found.",
                fallback_answer=narr.format_assistant_reply(
                    f"No {type_name.lower()}s are currently flagged as high risk.",
                    [],
                ),
            )
        bullets = [
            narr.high_risk_bullet(
                asset_tag=item.asset_tag,
                asset_type=item.asset_type_name,
                department_name=item.department_name,
                health_pct=int(item.health_score * 100),
            )
            for item in filtered[:5]
        ]
        sources = [
            {"label": item.asset_tag, "asset_id": item.asset_id, "url": f"/assets/{item.asset_id}"}
            for item in filtered[:5]
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"High-risk {type_name.lower()}s:",
                bullets,
            ),
            sources=sources,
            ollama_validation="strict",
        )

    def get_asset_department(self, asset_tag: str) -> dict:
        asset = self.asset_repo.get_by_tag(asset_tag.upper())
        if not asset:
            assets, _ = self.asset_repo.search(page=1, page_size=1, asset_tag=asset_tag)
            asset = assets[0] if assets else None
        if not asset:
            return self._result(
                data_text=f"No asset matched '{asset_tag}'.",
                fallback_answer=narr.format_assistant_reply(
                    f"I couldn't find asset {asset_tag}.",
                    [],
                ),
            )

        department = self.department_repo.get_by_id(asset.current_department_id)
        dept_name = department.name if department else "Unknown"
        answer = narr.asset_department_answer(
            asset_tag=asset.asset_tag,
            asset_name=asset.name,
            department_name=dept_name,
        )
        return self._result(
            data_text=f"{asset.asset_tag} -> {dept_name}",
            fallback_answer=answer,
            ollama_validation="minimal",
            sources=[
                {
                    "label": asset.asset_tag,
                    "asset_id": str(asset.id),
                    "url": f"/assets/{asset.id}",
                }
            ],
        )

    def get_asset_assignee(self, asset_tag: str) -> dict:
        asset = self.asset_repo.get_by_tag(asset_tag.upper())
        if not asset:
            assets, _ = self.asset_repo.search(page=1, page_size=1, asset_tag=asset_tag)
            asset = assets[0] if assets else None
        if not asset:
            return self._result(
                data_text=f"No asset matched '{asset_tag}'.",
                fallback_answer=narr.format_assistant_reply(
                    f"I couldn't find asset {asset_tag}.",
                    [],
                ),
            )

        employee_name: str | None = None
        if asset.current_assigned_employee_id:
            employee = self.employee_repo.get_by_id(asset.current_assigned_employee_id)
            if employee:
                employee_name = narr.employee_display(employee.first_name, employee.last_name)

        answer = narr.asset_assignee_answer(
            asset_tag=asset.asset_tag,
            asset_name=asset.name,
            employee_name=employee_name,
        )
        return self._result(
            data_text=f"{asset.asset_tag} assignee={employee_name or 'unassigned'}",
            fallback_answer=answer,
            ollama_validation="minimal",
            sources=[
                {
                    "label": asset.asset_tag,
                    "asset_id": str(asset.id),
                    "url": f"/assets/{asset.id}?tab=allocations",
                }
            ],
        )

    def get_clarification(self) -> dict:
        return self._result(
            data_text="Clarification requested.",
            fallback_answer=narr.assistant_clarify_message(),
            sources=[],
            skip_ollama=True,
        )

    def get_fleet_counts(self, message: str = "") -> dict:
        total_active_assets = self.dashboard_repo.count_assets(active_only=True)
        total_active_employees = self.dashboard_repo.count_employees(active_only=True)
        total_active_departments = self.dashboard_repo.count_departments(active_only=True)
        maintenance_due_count = self.dashboard_repo.maintenance_due_count()
        lower = message.lower()
        bullets = [
            narr.fleet_count_bullet("active assets", total_active_assets),
            narr.fleet_count_bullet("active employees", total_active_employees),
            narr.fleet_count_bullet("departments", total_active_departments),
            narr.fleet_count_bullet("overdue maintenance items", maintenance_due_count),
        ]

        matched_type: str | None = None
        for alias, type_name in _ASSET_TYPE_ALIASES.items():
            if alias in lower:
                matched_type = type_name
                break

        if matched_type:
            count = self.dashboard_repo.count_assets_by_type_name(matched_type)
            bullets.append(narr.fleet_count_bullet(f"{matched_type.lower()}s", count))
        elif any(k in lower for k in ("type", "types", "breakdown", "laptop", "server")):
            for type_name, count in self.dashboard_repo.assets_by_type()[:5]:
                bullets.append(narr.fleet_count_bullet(type_name.lower() + "s", count))

        intro = "Here's what I found in your fleet:"
        if matched_type:
            intro = f"Here's the count for {matched_type.lower()}s and related fleet stats:"
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(intro, bullets),
            sources=[],
        )

    def get_high_risk_assets(self) -> dict:
        if not self.predictions.is_cache_warm():
            return self._scoring_required()

        high_risk = self.predictions.get_high_risk(limit=5)
        if not high_risk.items:
            return self._result(
                data_text="No high-risk assets in the current scoring run.",
                fallback_answer=narr.format_assistant_reply(
                    "Good news — no assets are flagged as high risk right now.",
                    [],
                ),
                sources=[],
            )

        bullets = [
            narr.high_risk_bullet(
                asset_tag=item.asset_tag,
                asset_type=item.asset_type_name,
                department_name=item.department_name,
                health_pct=int(item.health_score * 100),
            )
            for item in high_risk.items
        ]
        sources = [
            {"label": item.asset_tag, "asset_id": item.asset_id, "url": f"/assets/{item.asset_id}"}
            for item in high_risk.items
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"I found {len(bullets)} high-risk asset{'s' if len(bullets) != 1 else ''}:",
                bullets,
            ),
            sources=sources,
            ollama_validation="strict",
        )

    def get_worst_health_assets(self) -> dict:
        if not self.predictions.is_cache_warm():
            return self._scoring_required()

        ranked = sorted(self.predictions.list_latest_predictions(), key=lambda p: p.health_score)[:5]
        if not ranked:
            return self._scoring_required()

        bullets = [
            narr.high_risk_bullet(
                asset_tag=p.asset_tag or "",
                asset_type=p.asset_type_name,
                department_name=p.department_name,
                health_pct=int(p.health_score * 100),
            )
            for p in ranked
        ]
        sources = [
            {"label": p.asset_tag or p.asset_id, "asset_id": p.asset_id, "url": f"/assets/{p.asset_id}"}
            for p in ranked
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                "These assets have the lowest predicted health:",
                bullets,
            ),
            sources=sources,
            ollama_validation="strict",
        )

    def get_maintenance_recommendations(self) -> dict:
        recs = self.recommendations.list_recommendations(limit=5)
        if not recs.items:
            if not self.predictions.is_cache_warm():
                return self._result(
                    data_text="No recommendations; cache empty.",
                    fallback_answer=narr.format_assistant_reply(
                        "No urgent maintenance items from overdue work orders.",
                        [
                            "Run AI scoring on the dashboard to include AI health alerts.",
                        ],
                    ),
                    sources=[],
                )
            return self._result(
                data_text="No maintenance recommendations at this time.",
                fallback_answer=narr.format_assistant_reply(
                    "Nothing urgent right now — your fleet looks clear on maintenance.",
                    [],
                ),
                sources=[],
            )

        bullets = [
            f"{r.title} ({r.asset_tag})." for r in recs.items
        ]
        sources = [
            {
                "label": r.asset_tag,
                "asset_id": r.asset_id,
                "url": f"/assets/{r.asset_id}?tab=maintenance",
            }
            for r in recs.items
        ]
        return self._result(
            data_text=" | ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"Here are the top {len(bullets)} maintenance priorities:",
                bullets,
            ),
            sources=sources,
        )

    def get_recent_transfers(self) -> dict:
        rows = self.dashboard_repo.recent_transfers(limit=5)
        if not rows:
            return self._result(
                data_text="No recent transfers found.",
                fallback_answer=narr.format_assistant_reply(
                    "No recent transfers in the activity feed.",
                    [],
                ),
                sources=[],
            )

        bullets = []
        sources = []
        for row in rows:
            asset = row.asset
            to_name = row.to_department.name
            headline = f"{asset.name} transferred to {to_name}"
            bullets.append(narr.transfer_bullet(headline=headline, asset_tag=asset.asset_tag))
            sources.append(
                {
                    "label": asset.asset_tag,
                    "asset_id": str(row.asset_id),
                    "url": f"/assets/{row.asset_id}?tab=timeline",
                }
            )
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply("Recent transfers:", bullets),
            sources=sources,
        )

    def get_warranty_expiring(self) -> dict:
        assets = self.dashboard_repo.warranty_expiring_soon(within_days=30, limit=5)
        if not assets:
            return self._result(
                data_text="No warranties expiring in the next 30 days.",
                fallback_answer=narr.format_assistant_reply(
                    "No warranties are expiring in the next 30 days.",
                    [],
                ),
                sources=[],
            )

        bullets = [
            narr.warranty_expiring_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                expiry=a.warranty_expiry,  # type: ignore[arg-type]
            )
            for a in assets
            if a.warranty_expiry
        ]
        sources = [
            {"label": a.asset_tag, "asset_id": str(a.id), "url": f"/assets/{a.id}"}
            for a in assets
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                "Warranties expiring within 30 days:",
                bullets,
            ),
            sources=sources,
        )

    def search_assets(self, message: str) -> dict:
        query = extract_search_term(message)
        tokens = re.findall(r"[A-Za-z0-9-]+", message)
        location_query = None
        for token in tokens:
            if token.lower() in ("floor", "building", "room", "hq", "lab", "warehouse"):
                location_query = " ".join(tokens[tokens.index(token) : tokens.index(token) + 3])
                break

        if location_query:
            result = self.assets.search(page=1, page_size=5, current_location=location_query)
        elif query:
            result = self.assets.search(
                page=1,
                page_size=5,
                name=query if "-" not in query else None,
                asset_tag=query if "-" in query else None,
            )
            if not result.items:
                result = self.assets.search(page=1, page_size=5, name=query)
        else:
            return self._result(
                data_text="No search query detected.",
                fallback_answer=narr.assistant_capabilities_message(),
                sources=[],
            )

        if not result.items:
            return self._result(
                data_text=f"No assets matched '{query or location_query}'.",
                fallback_answer=narr.format_assistant_reply(
                    f"I couldn't find assets matching '{query or location_query}'.",
                    ["Try an asset name, tag (e.g. IT-LAP-0001), or location keyword."],
                ),
                sources=[],
            )

        bullets = [
            narr.asset_list_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                status=a.current_status.value if hasattr(a.current_status, "value") else str(a.current_status),
            )
            for a in result.items
        ]
        sources = [
            {"label": a.asset_tag, "asset_id": str(a.id), "url": f"/assets/{a.id}"}
            for a in result.items
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply("Matching assets:", bullets),
            sources=sources,
        )

    def get_help(self) -> dict:
        return self._result(
            data_text="Assistant capabilities",
            fallback_answer=narr.assistant_capabilities_message(),
            sources=[],
            skip_ollama=True,
        )

    def get_healthy_assets(self) -> dict:
        if not self.predictions.is_cache_warm():
            return self._scoring_required()

        latest = self.predictions.list_latest_predictions()
        ranked = sorted(
            [p for p in latest if p.health_score >= 0.8],
            key=lambda p: p.health_score,
            reverse=True,
        )[:5]

        if not ranked:
            ranked = sorted(latest, key=lambda p: p.health_score, reverse=True)[:5]

        if not ranked:
            return self._result(
                data_text="No healthy assets found in the current scoring run.",
                fallback_answer=narr.format_assistant_reply(
                    "I couldn't find health metrics for any assets. Please run AI scoring first.",
                    [],
                ),
                sources=[],
            )

        bullets = [
            f"{p.asset_name or p.asset_tag} — health is excellent at {int(p.health_score * 100)}% ({p.asset_tag})"
            for p in ranked
        ]
        sources = [
            {"label": p.asset_tag or p.asset_id, "asset_id": p.asset_id, "url": f"/assets/{p.asset_id}"}
            for p in ranked
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                "These assets are in good condition with high predicted health:",
                bullets,
            ),
            sources=sources,
            ollama_validation="strict",
        )

    def get_overdue_maintenance(self) -> dict:
        rows = self.dashboard_repo.maintenance_due_items(limit=8)
        if not rows:
            return self._result(
                data_text="No overdue maintenance.",
                fallback_answer=narr.format_assistant_reply(
                    "No assets have overdue scheduled maintenance right now.",
                    [],
                ),
            )

        bullets = [
            narr.overdue_maintenance_bullet(
                asset_tag=asset.asset_tag,
                maintenance_type=record.maintenance_type.value,
                scheduled_date=record.scheduled_date,
            )
            for record, asset in rows
        ]
        sources = self._asset_sources([asset for _, asset in rows])
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"{len(bullets)} asset{'s' if len(bullets) != 1 else ''} with overdue maintenance:",
                bullets,
            ),
            sources=sources,
        )

    def get_assets_in_maintenance(self) -> dict:
        assets = self.dashboard_repo.assets_in_maintenance(limit=8)
        if not assets:
            return self._result(
                data_text="No assets in maintenance.",
                fallback_answer=narr.format_assistant_reply(
                    "No assets are currently marked as in maintenance.",
                    [],
                ),
            )

        bullets = [
            narr.asset_list_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                status=AssetStatus.IN_MAINTENANCE.value,
            )
            for a in assets
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                "Assets currently in maintenance:",
                bullets,
            ),
            sources=self._asset_sources(assets),
        )

    def get_recent_allocations(self) -> dict:
        rows = self.dashboard_repo.recent_allocations(limit=8)
        if not rows:
            return self._result(
                data_text="No recent allocations.",
                fallback_answer=narr.format_assistant_reply("No recent asset assignments found.", []),
            )

        bullets = []
        sources = []
        for row in rows:
            asset = row.asset
            employee = row.employee
            emp_name = narr.employee_display(employee.first_name, employee.last_name)
            bullets.append(
                narr.allocation_activity_bullet(
                    asset_tag=asset.asset_tag,
                    employee_name=emp_name,
                    action=row.action.value,
                )
            )
            sources.append(
                {
                    "label": asset.asset_tag,
                    "asset_id": str(asset.id),
                    "url": f"/assets/{asset.id}?tab=allocations",
                }
            )
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply("Recent asset assignments:", bullets),
            sources=sources,
        )

    def get_recent_completed_maintenance(self) -> dict:
        rows = self.dashboard_repo.recent_completed_maintenance(limit=8)
        if not rows:
            return self._result(
                data_text="No completed maintenance.",
                fallback_answer=narr.format_assistant_reply(
                    "No recently completed maintenance records found.",
                    [],
                ),
            )

        bullets = [
            f"{asset.asset_tag} — {record.maintenance_type.value.title()} completed "
            f"{record.completed_date.isoformat() if record.completed_date else 'recently'}"
            for record, asset in rows
        ]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                "Recently completed maintenance:",
                bullets,
            ),
            sources=self._asset_sources([asset for _, asset in rows]),
        )

    def get_department_assets(self, message: str) -> dict:
        query = extract_department_query(message)
        if not query:
            dept_rows = self.dashboard_repo.assets_by_department()
            if not dept_rows:
                return self._result(
                    data_text="No departments found.",
                    fallback_answer=narr.format_assistant_reply(
                        "I couldn't find any departments.",
                        [],
                    ),
                )
            bullets = [
                narr.department_summary_bullet(
                    department_name=name,
                    asset_count=count,
                    employee_count=self.department_repo.count_active_employees(
                        uuid.UUID(dep_id)
                    ),
                )
                for dep_id, name, count in dept_rows[:6]
            ]
            return self._result(
                data_text="; ".join(bullets),
                fallback_answer=narr.format_assistant_reply(
                    "Assets by department:",
                    bullets,
                ),
            )

        department = self.department_repo.find_best_match(query)
        if not department:
            return self._result(
                data_text=f"No department matched '{query}'.",
                fallback_answer=narr.format_assistant_reply(
                    f"I couldn't find a department matching '{query}'.",
                    ["Try the full department name, e.g. Information Technology."],
                ),
            )

        assets, total = self.asset_repo.search(
            page=1,
            page_size=8,
            current_department_id=department.id,
        )
        emp_count = self.department_repo.count_active_employees(department.id)
        summary = narr.department_summary_bullet(
            department_name=department.name,
            asset_count=total,
            employee_count=emp_count,
        )
        if not assets:
            return self._result(
                data_text=summary,
                fallback_answer=narr.format_assistant_reply(summary, []),
            )

        bullets = [
            narr.asset_list_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                status=a.current_status.value,
            )
            for a in assets
        ]
        return self._result(
            data_text=f"{summary}; " + "; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"{department.name} ({total} assets):",
                bullets,
            ),
            sources=self._asset_sources(assets),
        )

    def get_employee_assets(self, message: str) -> dict:
        query = extract_employee_query(message)
        if not query:
            return self._result(
                data_text="No employee name detected.",
                fallback_answer=narr.format_assistant_reply(
                    "Tell me which employee to look up.",
                    ["Example: What assets are assigned to Jane Smith?"],
                ),
            )

        employee = self.employee_repo.find_best_match(query)
        if not employee:
            return self._result(
                data_text=f"No employee matched '{query}'.",
                fallback_answer=narr.format_assistant_reply(
                    f"I couldn't find an employee matching '{query}'.",
                    ["Try first and last name or employee code."],
                ),
            )

        assets = self.asset_repo.list_assigned_to_employee(employee.id, limit=8)
        emp_name = narr.employee_display(employee.first_name, employee.last_name)
        intro = narr.employee_assets_intro(
            employee_name=emp_name,
            asset_count=len(assets),
        )
        if not assets:
            return self._result(data_text=intro, fallback_answer=intro)

        bullets = [
            narr.asset_list_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                status=a.current_status.value,
            )
            for a in assets
        ]
        return self._result(
            data_text=f"{intro} " + "; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(intro, bullets),
            sources=self._asset_sources(assets),
        )

    def get_assets_by_status(self, message: str) -> dict:
        status_key = extract_status_query(message)
        if not status_key:
            return self._result(
                data_text="No status detected.",
                fallback_answer=narr.format_assistant_reply(
                    "Which status should I filter by?",
                    ["Try: available, assigned, or in maintenance."],
                ),
            )

        status = AssetStatus(status_key)
        assets, total = self.asset_repo.search(
            page=1,
            page_size=8,
            current_status=status,
        )
        label = status.value.replace("_", " ").lower()
        if not assets:
            return self._result(
                data_text=f"No {label} assets.",
                fallback_answer=narr.format_assistant_reply(
                    f"No assets are currently {label}.",
                    [],
                ),
            )

        bullets = [
            narr.asset_list_bullet(
                asset_name=a.name,
                asset_tag=a.asset_tag,
                status=a.current_status.value,
            )
            for a in assets
        ]
        return self._result(
            data_text=f"{total} {label} assets; " + "; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"Showing {len(bullets)} of {total} {label} assets:",
                bullets,
            ),
            sources=self._asset_sources(assets),
        )

    def get_asset_health_detail(self, message: str) -> dict:
        tag = extract_asset_tag(message)
        asset = self.asset_repo.get_by_tag(tag) if tag else None
        if not asset and tag:
            assets, _ = self.asset_repo.search(page=1, page_size=1, asset_tag=tag)
            asset = assets[0] if assets else None

        if not asset:
            return self._result(
                data_text="No asset tag found in question.",
                fallback_answer=narr.format_assistant_reply(
                    "Include an asset tag so I can look up health data.",
                    ["Example: What is the health of IT-LAP-0001?"],
                ),
            )

        prediction = self.predictions.get_cached_prediction(asset.id)
        if prediction is None:
            history = self.health_repo.get_latest_prediction_for_asset(asset.id)
            if history and history.health_score is not None:
                meta = history.prediction_metadata or {}
                score = float(history.health_score)
                risk = meta.get("risk_level", "UNKNOWN")
            else:
                return self._scoring_required()
        else:
            score = prediction.health_score
            risk = prediction.risk_level.value if hasattr(prediction.risk_level, "value") else str(prediction.risk_level)

        _, band_label = narr.health_band_from_score(score)
        health_pct = int(score * 100)
        summary = narr.asset_health_summary_bullet(
            asset_tag=asset.asset_tag,
            health_pct=health_pct,
            risk_level=risk,
            band_label=band_label,
        )

        history_rows, _ = self.health_repo.list_by_asset(asset.id, page=1, page_size=4)
        trend_bullets = [
            narr.health_trend_bullet(
                recorded_at=row.recorded_at.date().isoformat(),
                health_pct=int(float(row.health_score) * 100),
            )
            for row in history_rows
            if row.health_score is not None
        ]
        bullets = [summary, *trend_bullets[:3]]
        return self._result(
            data_text="; ".join(bullets),
            fallback_answer=narr.format_assistant_reply(
                f"Health for {asset.asset_tag} ({asset.name}):",
                bullets,
            ),
            ollama_validation="relaxed",
            sources=[
                {
                    "label": asset.asset_tag,
                    "asset_id": str(asset.id),
                    "url": f"/assets/{asset.id}?tab=health",
                }
            ],
        )
