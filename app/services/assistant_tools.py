from __future__ import annotations

import re

from app.repositories.dashboard_repository import DashboardRepository
from app.services import narrative as narr
from app.services.asset_service import AssetService
from app.services.dashboard_service import DashboardService
from app.services.prediction_service import PredictionService, get_prediction_cache
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
    ) -> None:
        self.dashboard = dashboard_service
        self.assets = asset_service
        self.predictions = prediction_service
        self.recommendations = recommendation_service
        self.dashboard_repo = dashboard_repository

    def _scoring_required(self) -> dict:
        return {
            "data_text": "Prediction cache is empty.",
            "fallback_answer": narr.scoring_required_message(),
            "sources": [],
            "cache_required": True,
        }

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
        return {
            "data_text": data_text,
            "fallback_answer": fallback,
            "sources": [],
        }

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
        return {
            "data_text": "; ".join(bullets),
            "fallback_answer": narr.format_assistant_reply(intro, bullets),
            "sources": [],
        }

    def get_high_risk_assets(self) -> dict:
        if not self.predictions.is_cache_warm():
            return self._scoring_required()

        high_risk = self.predictions.get_high_risk(limit=5)
        if not high_risk.items:
            return {
                "data_text": "No high-risk assets in the current scoring run.",
                "fallback_answer": narr.format_assistant_reply(
                    "Good news — no assets are flagged as high risk right now.",
                    [],
                ),
                "sources": [],
            }

        bullets = [
            narr.high_risk_bullet(
                asset_name=item.asset_name or item.asset_tag,
                asset_tag=item.asset_tag,
                health_pct=int(item.health_score * 100),
            )
            for item in high_risk.items
        ]
        sources = [
            {"label": item.asset_tag, "asset_id": item.asset_id, "url": f"/assets/{item.asset_id}"}
            for item in high_risk.items
        ]
        return {
            "data_text": "; ".join(bullets),
            "fallback_answer": narr.format_assistant_reply(
                f"I found {len(bullets)} high-risk asset{'s' if len(bullets) != 1 else ''}:",
                bullets,
            ),
            "sources": sources,
        }

    def get_worst_health_assets(self) -> dict:
        if not self.predictions.is_cache_warm():
            return self._scoring_required()

        ranked = sorted(get_prediction_cache().values(), key=lambda p: p.health_score)[:5]
        if not ranked:
            return self._scoring_required()

        bullets = [
            narr.high_risk_bullet(
                asset_name=p.asset_name or p.asset_tag or "Asset",
                asset_tag=p.asset_tag or "",
                health_pct=int(p.health_score * 100),
            )
            for p in ranked
        ]
        sources = [
            {"label": p.asset_tag or p.asset_id, "asset_id": p.asset_id, "url": f"/assets/{p.asset_id}"}
            for p in ranked
        ]
        return {
            "data_text": "; ".join(bullets),
            "fallback_answer": narr.format_assistant_reply(
                "These assets have the lowest predicted health:",
                bullets,
            ),
            "sources": sources,
        }

    def get_maintenance_recommendations(self) -> dict:
        recs = self.recommendations.list_recommendations(limit=5)
        if not recs.items:
            if not self.predictions.is_cache_warm():
                return {
                    "data_text": "No recommendations; cache empty.",
                    "fallback_answer": narr.format_assistant_reply(
                        "No urgent maintenance items from overdue work orders.",
                        [
                            "Run AI scoring on the dashboard to include AI health alerts.",
                        ],
                    ),
                    "sources": [],
                }
            return {
                "data_text": "No maintenance recommendations at this time.",
                "fallback_answer": narr.format_assistant_reply(
                    "Nothing urgent right now — your fleet looks clear on maintenance.",
                    [],
                ),
                "sources": [],
            }

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
        return {
            "data_text": " | ".join(bullets),
            "fallback_answer": narr.format_assistant_reply(
                f"Here are the top {len(bullets)} maintenance priorities:",
                bullets,
            ),
            "sources": sources,
        }

    def get_recent_transfers(self) -> dict:
        rows = self.dashboard_repo.recent_transfers(limit=5)
        if not rows:
            return {
                "data_text": "No recent transfers found.",
                "fallback_answer": narr.format_assistant_reply(
                    "No recent transfers in the activity feed.",
                    [],
                ),
                "sources": [],
            }

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
        return {
            "data_text": "; ".join(bullets),
            "fallback_answer": narr.format_assistant_reply("Recent transfers:", bullets),
            "sources": sources,
        }

    def get_warranty_expiring(self) -> dict:
        assets = self.dashboard_repo.warranty_expiring_soon(within_days=30, limit=5)
        if not assets:
            return {
                "data_text": "No warranties expiring in the next 30 days.",
                "fallback_answer": narr.format_assistant_reply(
                    "No warranties are expiring in the next 30 days.",
                    [],
                ),
                "sources": [],
            }

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
        return {
            "data_text": "; ".join(bullets),
            "fallback_answer": narr.format_assistant_reply(
                "Warranties expiring within 30 days:",
                bullets,
            ),
            "sources": sources,
        }

    def search_assets(self, message: str) -> dict:
        tokens = re.findall(r"[A-Za-z0-9-]+", message)
        stop_words = {
            "show",
            "which",
            "assets",
            "asset",
            "find",
            "search",
            "where",
            "many",
            "how",
            "the",
            "are",
            "there",
            "what",
            "list",
        }
        query = next((t for t in tokens if len(t) >= 3 and t.lower() not in stop_words), "")
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
            return {
                "data_text": "No search query detected.",
                "fallback_answer": narr.assistant_capabilities_message(),
                "sources": [],
            }

        if not result.items:
            return {
                "data_text": f"No assets matched '{query or location_query}'.",
                "fallback_answer": narr.format_assistant_reply(
                    f"I couldn't find assets matching '{query or location_query}'.",
                    ["Try an asset name, tag (e.g. IT-LAP-0001), or location keyword."],
                ),
                "sources": [],
            }

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
        return {
            "data_text": "; ".join(bullets),
            "fallback_answer": narr.format_assistant_reply("Matching assets:", bullets),
            "sources": sources,
        }

    def get_help(self) -> dict:
        return {
            "data_text": "Assistant capabilities",
            "fallback_answer": narr.assistant_capabilities_message(),
            "sources": [],
        }

    def get_healthy_assets(self) -> dict:
        if not self.predictions.is_cache_warm():
            return self._scoring_required()

        ranked = sorted(
            [p for p in get_prediction_cache().values() if p.health_score >= 0.8],
            key=lambda p: p.health_score,
            reverse=True,
        )[:5]

        if not ranked:
            ranked = sorted(get_prediction_cache().values(), key=lambda p: p.health_score, reverse=True)[:5]

        if not ranked:
            return {
                "data_text": "No healthy assets found in the current scoring run.",
                "fallback_answer": narr.format_assistant_reply(
                    "I couldn't find health metrics for any assets. Please run AI scoring first.",
                    [],
                ),
                "sources": [],
            }

        bullets = [
            f"{p.asset_name or p.asset_tag} — health is excellent at {int(p.health_score * 100)}% ({p.asset_tag})"
            for p in ranked
        ]
        sources = [
            {"label": p.asset_tag or p.asset_id, "asset_id": p.asset_id, "url": f"/assets/{p.asset_id}"}
            for p in ranked
        ]
        return {
            "data_text": "; ".join(bullets),
            "fallback_answer": narr.format_assistant_reply(
                "These assets are in good condition with high predicted health:",
                bullets,
            ),
            "sources": sources,
        }
