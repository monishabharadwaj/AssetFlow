from __future__ import annotations

import uuid

from app.core.config import settings
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.explanation import PredictionExplanation, RootCauseResponse
from app.schemas.intelligence import HealthPredictionResponse
from app.services import narrative as narr
from app.services.ollama_client import ollama_generate
from app.services.prediction_explanation_service import PredictionExplanationService
from app.services.prediction_service import PredictionService


class RootCauseService:
    def __init__(
        self,
        prediction_service: PredictionService,
        explanation_service: PredictionExplanationService,
        timeline_repository: TimelineRepository | None = None,
    ) -> None:
        self.prediction_service = prediction_service
        self.explanation_service = explanation_service
        self.timeline_repository = timeline_repository

    def _instant_summary(self, explanation: PredictionExplanation) -> str:
        if explanation.enterprise_brief:
            brief = explanation.enterprise_brief
            return (
                f"{brief.what_happened} {brief.recommended_action} "
                f"Priority: {brief.priority}. Estimated downtime: {brief.estimated_downtime}."
            )
        return explanation.summary

    def _timeline_context(self, asset_id: uuid.UUID) -> str:
        if self.timeline_repository is None:
            return ""
        lines: list[str] = []
        for maint in self.timeline_repository.maintenance_for_asset(asset_id)[:2]:
            lines.append(
                f"Maintenance ({maint.maintenance_type.value}): {maint.status.value} — "
                f"{maint.description[:80]}"
            )
        for transfer in self.timeline_repository.transfers_for_asset(asset_id)[:2]:
            lines.append(
                f"Transfer: {transfer.from_department.name} → {transfer.to_department.name} "
                f"({transfer.to_location})"
            )
        return "\n".join(lines)

    async def get_root_cause(
        self,
        asset_id: uuid.UUID,
        *,
        use_llm: bool = False,
    ) -> RootCauseResponse:
        prediction = self.prediction_service.get_cached_prediction(asset_id)
        if prediction is None:
            prediction = self.prediction_service.predict_asset(asset_id, persist=False)

        features = self.prediction_service.feature_service.extract_asset_features(asset_id)
        explanation = self.explanation_service.build(
            features=features,
            health_score=prediction.health_score,
            risk_level=prediction.risk_level,
            asset_name=prediction.asset_name or prediction.asset_tag or "Asset",
        )


        summary = self._instant_summary(explanation)
        source = "template"
        timeline_ctx = self._timeline_context(asset_id)

        if use_llm and settings.assistant_use_ollama:
            brief = explanation.enterprise_brief
            prompt = (
                "You are an enterprise asset operations advisor. Write a clear, non-technical "
                "brief in 3-5 sentences for an IT administrator.\n"
                "Use ONLY the facts below. Do not mention ML, models, or algorithms.\n\n"
            )
            if brief:
                prompt += (
                    f"Asset: {prediction.asset_name} ({prediction.asset_tag})\n"
                    f"What happened: {brief.what_happened}\n"
                    f"Why: {brief.why_predicted}\n"
                    f"Business impact: {brief.business_impact}\n"
                    f"Recommended action: {brief.recommended_action}\n"
                    f"Priority: {brief.priority}\n"
                    f"Downtime: {brief.estimated_downtime}\n"
                )
            else:
                prompt += f"Summary: {explanation.summary}\n"
            if timeline_ctx:
                prompt += f"\nRecent events:\n{timeline_ctx}\n"
            try:
                llm_text = await ollama_generate(prompt)
                if llm_text:
                    summary = llm_text
                    source = "ollama"
            except Exception:
                pass

        return RootCauseResponse(
            asset_id=prediction.asset_id,
            asset_tag=prediction.asset_tag,
            asset_name=prediction.asset_name,
            health_score=prediction.health_score,
            risk_level=prediction.risk_level.value,
            root_cause_summary=summary,
            source=source,
            factors=explanation.factors,
            anomaly_detected=explanation.anomaly_detected,
            enterprise_brief=explanation.enterprise_brief,
        )
