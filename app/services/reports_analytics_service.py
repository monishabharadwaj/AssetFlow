from __future__ import annotations

import asyncio
import json
import re
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from app.core.access_scope import AccessContext
from app.core.config import settings
from app.repositories.asset_repository import AssetRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.schemas.reports_analytics import (
    ChartPoint,
    CostAnalytics,
    DriftAnalytics,
    MaintenanceAnalytics,
    OrgBenchmarks,
    ReportInsightSection,
    ReplacementAnalytics,
    ReplacementPlanEnriched,
    ReportsAnalyticsResponse,
)
from app.services.cost_optimization_service import CostOptimizationService
from app.services.dashboard_service import DashboardService
from app.services.drift_monitoring_service import DriftMonitoringService
from app.services.intelligence_pipeline_service import IntelligencePipelineService
from app.services.maintenance_scheduling_service import MaintenanceSchedulingService
from app.services.ollama_client import ollama_generate
from app.services.prediction_service import get_prediction_cache
from app.services.recommendation_service import RecommendationService
from app.services.replacement_planning_service import ReplacementPlanningService


def compute_org_benchmarks(
    scope: AccessContext | None,
    dept_avg_health_pct: int,
    all_predictions: list,
) -> OrgBenchmarks | None:
    """Anonymous org-wide aggregates for department-scoped users only."""
    if scope is None or scope.is_org_wide:
        return None
    if not all_predictions:
        org_avg_pct = 0
        org_high_risk = 0
    else:
        org_avg_pct = int(
            round(sum(p.health_score for p in all_predictions) / len(all_predictions) * 100)
        )
        org_high_risk = sum(1 for p in all_predictions if p.risk_level.value == "HIGH")
    return OrgBenchmarks(
        org_avg_fleet_health_pct=org_avg_pct,
        dept_vs_org_health_delta=dept_avg_health_pct - org_avg_pct,
        org_high_risk_assets=org_high_risk,
    )


class ReportsAnalyticsService:
    def __init__(
        self,
        dashboard_service: DashboardService,
        recommendation_service: RecommendationService,
        drift_service: DriftMonitoringService,
        replacement_service: ReplacementPlanningService,
        cost_service: CostOptimizationService,
        maintenance_service: MaintenanceSchedulingService,
        pipeline_service: IntelligencePipelineService,
        asset_repository: AssetRepository,
        maintenance_repository: MaintenanceRepository,
    ) -> None:
        self.dashboard = dashboard_service
        self.recommendations = recommendation_service
        self.drift = drift_service
        self.replacement = replacement_service
        self.cost = cost_service
        self.maintenance = maintenance_service
        self.pipeline = pipeline_service
        self.asset_repository = asset_repository
        self.maintenance_repository = maintenance_repository

    def _scoped_predictions(self, scope: AccessContext | None):
        cache = list(get_prediction_cache().values())
        department_id = scope.scoping_department_id() if scope else None
        if department_id is None:
            return cache
        allowed = self.asset_repository.filter_ids_by_department(
            [uuid.UUID(p.asset_id) for p in cache],
            department_id,
        )
        return [p for p in cache if uuid.UUID(p.asset_id) in allowed]

    async def build(self, *, use_ai: bool = False, scope: AccessContext | None = None) -> ReportsAnalyticsResponse:
        department_id = scope.scoping_department_id() if scope else None
        scope_label = (
            "Organization-wide"
            if scope is None or scope.is_org_wide
            else f"{scope.department_id} department scope"
        )
        summary = self.dashboard.get_summary(scope)
        predictions = self._scoped_predictions(scope)
        recs = self.recommendations.list_recommendations(limit=8, scope=scope)
        drift_data = self.drift.detect_drift(department_id=department_id)
        replacement_data = self.replacement.build_plan(limit=10, department_id=department_id)
        cost_data = self.cost.analyze(limit=10, department_id=department_id)
        schedule_data = self.maintenance.suggest_windows(limit=10, department_id=department_id)
        scoring = self.pipeline.get_status()

        high_risk = sum(1 for p in predictions if p.risk_level.value == "HIGH")
        medium_risk = sum(1 for p in predictions if p.risk_level.value == "MEDIUM")
        avg_health = (
            round(sum(p.health_score for p in predictions) / len(predictions), 3)
            if predictions
            else 0.0
        )

        kpis = {
            "active_assets": summary.total_active_assets,
            "high_risk_assets": high_risk,
            "maintenance_due": summary.maintenance_due_count,
            "drift_alerts": drift_data.total,
            "scored_assets": len(predictions),
            "avg_fleet_health_pct": int(avg_health * 100),
            "replacement_candidates": replacement_data.total,
        }

        drift_section = self._build_drift(drift_data, predictions)
        cost_section = self._build_cost(cost_data, department_id)
        replacement_section = self._build_replacement(replacement_data)
        maintenance_section = self._build_maintenance(schedule_data, predictions)
        kpis["estimated_annual_savings"] = cost_section.estimated_annual_savings
        benchmarks = compute_org_benchmarks(
            scope,
            int(avg_health * 100),
            list(get_prediction_cache().values()),
        )
        executive = self._build_executive_sections(
            summary=summary,
            predictions=predictions,
            recs=recs,
            drift=drift_section,
            cost=cost_section,
            replacement=replacement_section,
            maintenance=maintenance_section,
            kpis=kpis,
        )

        source = "analyst_template"
        if use_ai and settings.assistant_use_ollama:
            (
                enhanced_result,
                drift_insight,
                cost_insight,
                replacement_insight,
                maintenance_insight,
            ) = await asyncio.gather(
                self._enhance_with_llm(executive, drift_section, cost_section, replacement_section),
                self._llm_section(
                    "Health Drift",
                    drift_section.ai_insight,
                    [a.message for a in drift_data.alerts[:5]],
                ),
                self._llm_section(
                    "Cost Optimization",
                    cost_section.ai_insight,
                    cost_section.opportunities[:4],
                ),
                self._llm_section(
                    "Replacement Planning",
                    replacement_section.ai_insight,
                    [i.why_replace for i in replacement_section.items[:4]],
                ),
                self._llm_section(
                    "Maintenance Schedule",
                    maintenance_section.ai_insight,
                    [i.rationale for i in schedule_data.items[:4]],
                ),
                return_exceptions=True,
            )
            if isinstance(enhanced_result, list):
                executive = enhanced_result
                source = "ollama"
            drift_section.ai_insight = (
                drift_insight if isinstance(drift_insight, str) and drift_insight else drift_section.ai_insight
            )
            cost_section.ai_insight = (
                cost_insight if isinstance(cost_insight, str) and cost_insight else cost_section.ai_insight
            )
            replacement_section.ai_insight = (
                replacement_insight
                if isinstance(replacement_insight, str) and replacement_insight
                else replacement_section.ai_insight
            )
            maintenance_section.ai_insight = (
                maintenance_insight
                if isinstance(maintenance_insight, str) and maintenance_insight
                else maintenance_section.ai_insight
            )
            if source == "analyst_template" and any(
                isinstance(v, str) and v
                for v in (drift_insight, cost_insight, replacement_insight, maintenance_insight)
            ):
                source = "ollama"

        return ReportsAnalyticsResponse(
            generated_at=datetime.now(timezone.utc),
            scope_label=scope_label,
            use_ai=use_ai,
            source=source,
            ollama_enabled=settings.assistant_use_ollama,
            benchmarks=benchmarks,
            kpis=kpis,
            executive_sections=executive,
            drift=drift_section,
            cost=cost_section,
            replacement=replacement_section,
            maintenance=maintenance_section,
            scoring=scoring,
        )

    def _build_drift(self, drift_data, predictions) -> DriftAnalytics:
        deteriorating = [a for a in drift_data.alerts if a.health_delta < 0]
        improving = [
            p for p in predictions
            if p.explanation and p.explanation.health_delta and p.explanation.health_delta > 0.05
        ]
        health_chart = [
            ChartPoint(label=a.asset_tag or a.asset_name, value=round(a.health_delta * 100, 1))
            for a in deteriorating[:8]
        ]
        dept_scores: dict[str, list[float]] = defaultdict(list)
        for p in predictions:
            name = p.department_name or "Unknown"
            dept_scores[name].append(p.health_score)
        dept_comparison = [
            ChartPoint(label=name, value=round(sum(scores) / len(scores) * 100, 1))
            for name, scores in sorted(dept_scores.items(), key=lambda x: -len(x[1]))[:8]
        ]
        factors: list[str] = []
        for alert in deteriorating[:3]:
            factors.append(
                f"{alert.asset_tag}: health fell {abs(int(alert.health_delta * 100))}% — "
                f"likely driven by overdue maintenance or rising utilization."
            )
        ai_insight = (
            f"{len(deteriorating)} assets show meaningful health decline. "
            f"{len(improving)} assets improved since last scoring. "
            "Prioritize drift alerts before they become failures — schedule inspection within 7 days."
        )
        if not deteriorating:
            ai_insight = (
                "No significant negative drift detected in the current scoring window. "
                "Continue preventive maintenance to sustain fleet health."
            )
        return DriftAnalytics(
            alerts=drift_data.alerts,
            deteriorating=deteriorating,
            improving_count=len(improving),
            health_trend_chart=health_chart,
            department_comparison=dept_comparison,
            ai_insight=ai_insight,
            key_factors=factors or ["Fleet health is stable — no major drift drivers identified."],
        )

    def _build_cost(self, cost_data, department_id) -> CostAnalytics:
        distribution = [
            ChartPoint(label=i.asset_tag, value=round(i.tco_ratio * 100, 1), category=i.priority)
            for i in cost_data.items[:8]
        ]
        dept_costs: dict[str, float] = defaultdict(float)
        page = 1
        while page <= 3:
            assets, total = self.asset_repository.list(
                page=page, page_size=100, is_active=True, department_id=department_id
            )
            if not assets:
                break
            for asset in assets:
                dept_name = asset.current_department.name if asset.current_department else "Unknown"
                dept_costs[dept_name] += self.maintenance_repository.total_cost_for_asset(asset.id)
            if page * 100 >= total:
                break
            page += 1
        dept_chart = [
            ChartPoint(label=k, value=round(v, 0))
            for k, v in sorted(dept_costs.items(), key=lambda x: -x[1])[:8]
        ]
        savings = sum(i.maintenance_spend * 0.25 for i in cost_data.items if i.tco_ratio >= 0.3)
        opportunities = [i.recommendation for i in cost_data.items[:5]]
        ai_insight = (
            f"Identified ${savings:,.0f} in potential annual savings by replacing or rebalancing "
            f"high-TCO assets and consolidating maintenance for {len(cost_data.items)} flagged items."
        )
        if not cost_data.items:
            ai_insight = "Maintenance spend is proportionate to asset value — no urgent cost outliers."
        return CostAnalytics(
            items=cost_data.items,
            cost_distribution=distribution,
            department_costs=dept_chart,
            estimated_annual_savings=round(savings, 2),
            ai_insight=ai_insight,
            opportunities=opportunities,
        )

    def _build_replacement(self, replacement_data) -> ReplacementAnalytics:
        enriched: list[ReplacementPlanEnriched] = []
        for item in replacement_data.items:
            maint = self.maintenance_repository.total_cost_for_asset(uuid.UUID(item.asset_id))
            health_trend = "declining" if item.health_score is not None and item.health_score < 0.5 else "stable"
            repair_vs = (
                f"Repair path: estimated ${maint * 1.2:,.0f}/yr ongoing service. "
                f"Replace path: capital refresh now avoids {item.replace_within_months}mo reliability cliff."
            )
            delayed = (
                f"Delaying replacement on {item.asset_tag} increases downtime risk and may force "
                f"emergency procurement at premium cost."
            )
            enriched.append(
                ReplacementPlanEnriched(
                    **item.model_dump(),
                    why_replace=item.rationale,
                    remaining_useful_life_months=item.replace_within_months,
                    health_trend=health_trend,
                    maintenance_spend=round(maint, 2),
                    repair_vs_replace=repair_vs,
                    business_impact_if_delayed=delayed,
                )
            )
        ai_insight = (
            f"{len(enriched)} assets are candidates for lifecycle refresh. "
            "Replace HIGH priority units before end-of-life to avoid operational disruption."
        )
        if not enriched:
            ai_insight = "No assets currently meet replacement urgency thresholds."
        return ReplacementAnalytics(items=enriched, ai_insight=ai_insight)

    def _build_maintenance(self, schedule_data, predictions) -> MaintenanceAnalytics:
        priority = [
            ChartPoint(label=i.asset_tag, value=float(i.suggested_within_days), category="urgency")
            for i in schedule_data.items[:8]
        ]
        dept_load: dict[str, int] = defaultdict(int)
        for item in schedule_data.items:
            pred = next((p for p in predictions if p.asset_id == item.asset_id), None)
            dept = pred.department_name if pred and pred.department_name else "Unknown"
            dept_load[dept] += 1
        workload = [ChartPoint(label=k, value=float(v)) for k, v in sorted(dept_load.items(), key=lambda x: -x[1])]
        high_risk_unscheduled = sum(
            1 for p in predictions if p.risk_level.value == "HIGH"
        )
        skip_risk = (
            f"If scheduled maintenance is skipped on high-utilization assets, "
            f"{high_risk_unscheduled} high-risk units could fail within 30 days."
        )
        ai_insight = (
            f"Optimized schedule covers {len(schedule_data.items)} assets. "
            "Batch maintenance by department to reduce operational disruption."
        )
        return MaintenanceAnalytics(
            items=schedule_data.items,
            priority_ranking=priority,
            department_workload=workload,
            ai_insight=ai_insight,
            skip_risk_summary=skip_risk,
        )

    def _build_executive_sections(self, *, summary, predictions, recs, drift, cost, replacement, maintenance, kpis):
        high_risk_names = [p.asset_tag or p.asset_name for p in predictions if p.risk_level.value == "HIGH"][:5]
        return [
            ReportInsightSection(
                key="executive_summary",
                title="Executive Summary",
                summary=(
                    f"Fleet of {summary.total_active_assets} active assets at {kpis['avg_fleet_health_pct']}% "
                    f"average health with {kpis['high_risk_assets']} high-risk units requiring leadership attention."
                ),
                bullets=[
                    f"{summary.maintenance_due_count} maintenance items overdue",
                    f"{len(drift.deteriorating)} assets with negative health drift",
                    f"${cost.estimated_annual_savings:,.0f} potential cost savings identified",
                ],
            ),
            ReportInsightSection(
                key="fleet_health",
                title="Overall Fleet Health",
                summary=f"AI scored {len(predictions)} assets. Average health {kpis['avg_fleet_health_pct']}%.",
                bullets=[
                    f"High risk: {kpis['high_risk_assets']}",
                    f"Medium risk: {sum(1 for p in predictions if p.risk_level.value == 'MEDIUM')}",
                    f"Improving assets: {drift.improving_count}",
                ],
            ),
            ReportInsightSection(
                key="major_events",
                title="Major Events This Week",
                summary="Key operational signals from maintenance, drift, and lifecycle planning.",
                bullets=[
                    f"{summary.maintenance_due_count} overdue maintenance records",
                    f"{len(drift.alerts)} drift alerts generated",
                    f"{len(replacement.items)} replacement candidates flagged",
                ],
            ),
            ReportInsightSection(
                key="immediate_attention",
                title="Assets Requiring Immediate Attention",
                summary="Highest priority assets from AI risk scoring and overdue work.",
                bullets=high_risk_names or ["No critical assets — fleet within tolerance"],
            ),
            ReportInsightSection(
                key="maintenance_performance",
                title="Maintenance Performance",
                summary=maintenance.ai_insight,
                bullets=[i.rationale for i in maintenance.items[:4]] or ["No urgent maintenance windows"],
            ),
            ReportInsightSection(
                key="department_performance",
                title="Department-wise Performance",
                summary="Relative health and workload by department.",
                bullets=[f"{c.label}: {c.value}% avg health" for c in drift.department_comparison[:5]]
                or ["Department breakdown available after AI scoring"],
            ),
            ReportInsightSection(
                key="ai_observations",
                title="AI Observations",
                summary="Model-driven patterns from health predictions and utilization features.",
                bullets=drift.key_factors[:4],
            ),
            ReportInsightSection(
                key="risk_analysis",
                title="Risk Analysis",
                summary=f"{kpis['high_risk_assets']} assets classified HIGH risk by FT-Transformer model.",
                bullets=[r.title for r in recs.items[:4]] or ["Risk levels within normal range"],
            ),
            ReportInsightSection(
                key="predicted_issues",
                title="Predicted Issues",
                summary=maintenance.skip_risk_summary,
                bullets=[f"{i.asset_tag}: service within {i.suggested_within_days} days" for i in maintenance.items[:4]],
            ),
            ReportInsightSection(
                key="recommended_actions",
                title="Recommended Actions",
                summary="Prioritized actions for operations and finance leaders.",
                bullets=(
                    [r.title for r in recs.items[:3]]
                    + cost.opportunities[:2]
                    + [i.repair_vs_replace for i in replacement.items[:2]]
                )[:6]
                or ["Continue monitoring — no urgent actions"],
            ),
            ReportInsightSection(
                key="expected_impact",
                title="Expected Impact Next Week",
                summary=(
                    "If recommended actions are executed, expect reduced downtime risk and "
                    "stabilized health scores across high-utilization assets."
                ),
                bullets=[
                    "High-risk count should decrease after scheduled maintenance",
                    "Drift alerts should stabilize within one scoring cycle",
                    f"Potential ${cost.estimated_annual_savings:,.0f} cost avoidance if TCO actions taken",
                ],
            ),
        ]

    async def _enhance_with_llm(self, sections, drift, cost, replacement) -> list[ReportInsightSection] | None:
        facts = "\n".join(
            f"### {s.title}\nSummary: {s.summary}\nBullets: {'; '.join(s.bullets[:4])}"
            for s in sections
        )
        prompt = (
            "You are an enterprise asset management analyst preparing an executive report. "
            "For EACH section below, write a polished 2-3 sentence summary for leadership "
            "and up to 4 concise bullet points. Respond ONLY with valid JSON array:\n"
            '[{"key":"section_key","summary":"...","bullets":["..."]}, ...]\n'
            "Use the exact key values from the input. Do not omit any section.\n\n"
            + facts
        )
        try:
            text = await ollama_generate(prompt, timeout=45.0)
            if not text:
                return None
            match = re.search(r"\[[\s\S]*\]", text)
            if not match:
                return None
            parsed = json.loads(match.group())
            by_key = {item.get("key"): item for item in parsed if isinstance(item, dict)}
            enhanced: list[ReportInsightSection] = []
            for s in sections:
                item = by_key.get(s.key)
                if item and item.get("summary"):
                    enhanced.append(
                        ReportInsightSection(
                            key=s.key,
                            title=s.title,
                            summary=str(item["summary"]),
                            bullets=[str(b) for b in (item.get("bullets") or s.bullets)[:6]],
                        )
                    )
                else:
                    enhanced.append(s)
            return enhanced if any(e.summary != s.summary for e, s in zip(enhanced, sections)) else None
        except Exception:
            return None

    async def _llm_section(self, title: str, fallback: str, bullets: list[str]) -> str | None:
        if not bullets:
            return None
        prompt = (
            f"As an asset analyst, write 3-4 sentences explaining {title} for management. "
            f"Facts:\n" + "\n".join(f"- {b}" for b in bullets)
        )
        try:
            return await ollama_generate(prompt, timeout=25.0)
        except Exception:
            return None
