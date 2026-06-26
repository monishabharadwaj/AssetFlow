from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.operations import OperationalReportResponse
from app.services import narrative as narr
from app.services.cost_optimization_service import CostOptimizationService
from app.services.dashboard_service import DashboardService
from app.services.drift_monitoring_service import DriftMonitoringService
from app.services.ollama_client import ollama_generate
from app.services.prediction_service import get_prediction_cache
from app.services.recommendation_service import RecommendationService
from app.services.replacement_planning_service import ReplacementPlanningService


class ReportService:
    def __init__(
        self,
        dashboard_service: DashboardService,
        recommendation_service: RecommendationService,
        drift_service: DriftMonitoringService,
        replacement_service: ReplacementPlanningService,
        cost_service: CostOptimizationService,
    ) -> None:
        self.dashboard = dashboard_service
        self.recommendations = recommendation_service
        self.drift = drift_service
        self.replacement = replacement_service
        self.cost = cost_service

    async def generate_weekly_brief(self, *, use_llm: bool = False) -> OperationalReportResponse:
        generated_at = datetime.now(timezone.utc)
        summary_data = self.dashboard.get_summary()
        recs = self.recommendations.list_recommendations(limit=5)
        drift = self.drift.detect_drift()
        replacements = self.replacement.build_plan(limit=3)
        costs = self.cost.analyze(limit=3)
        cache = get_prediction_cache()
        high_risk_count = sum(1 for p in cache.values() if p.risk_level.value == "HIGH")

        sections = [
            f"Fleet: {summary_data.total_active_assets} active assets, "
            f"{summary_data.maintenance_due_count} overdue maintenance items.",
            f"AI scoring: {len(cache)} assets scored, {high_risk_count} high risk.",
            f"Drift alerts: {drift.total} assets with significant health decline.",
        ]
        if recs.items:
            sections.append(
                "Top maintenance priorities: "
                + "; ".join(f"{r.asset_name} ({r.priority.value})" for r in recs.items[:3])
            )
        if replacements.items:
            sections.append(
                "Replacement planning: "
                + "; ".join(f"{r.asset_name} within {r.replace_within_months}mo" for r in replacements.items)
            )
        if costs.items:
            sections.append(
                "Cost flags: "
                + "; ".join(f"{c.asset_name} TCO {c.tco_ratio:.0%}" for c in costs.items)
            )

        template_summary = narr.weekly_ops_brief_summary(
            total_assets=summary_data.total_active_assets,
            high_risk_count=high_risk_count,
            maintenance_due=summary_data.maintenance_due_count,
            drift_count=drift.total,
        )

        summary = template_summary
        source = "template"

        if use_llm and settings.assistant_use_ollama:
            prompt = (
                "You are an asset operations analyst. Write a concise weekly operations brief "
                "in 4-6 sentences for management. Use ONLY the facts below.\n\n"
                + "\n".join(f"- {s}" for s in sections)
            )
            try:
                llm_text = await ollama_generate(prompt)
                if llm_text:
                    summary = llm_text
                    source = "ollama"
            except Exception:
                pass

        return OperationalReportResponse(
            title="Weekly Operations Brief",
            generated_at=generated_at,
            summary=summary,
            sections=sections,
            source=source,
            metrics={
                "active_assets": summary_data.total_active_assets,
                "high_risk_assets": high_risk_count,
                "maintenance_due": summary_data.maintenance_due_count,
                "drift_alerts": drift.total,
                "scored_assets": len(cache),
            },
        )
