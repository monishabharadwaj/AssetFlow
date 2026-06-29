import { apiGet, apiPost } from "@/lib/api";
import type {
  HealthPredictionResponse,
  RecommendationListResponse,
  RootCauseResponse,
} from "@/lib/types/backend";
import type { Recommendation } from "@/lib/types/ui";

export async function fetchRecommendations(): Promise<Recommendation[]> {
  const data = await apiGet<RecommendationListResponse>("/intelligence/recommendations");
  return data.items.map((item, i) => ({
    id: item.asset_id || String(i),
    asset_id: item.asset_id,
    title: item.title,
    description: item.rationale,
    priority: item.priority,
    hint: item.rationale,
    asset_count: 1,
  }));
}

export function predictAssetHealth(assetId: string, persist = false) {
  return apiPost<HealthPredictionResponse>(`/intelligence/assets/${assetId}/predict?persist=${persist}`, {});
}

export function fetchAssetRootCause(assetId: string, useLlm = false) {
  return apiGet<RootCauseResponse>(`/intelligence/assets/${assetId}/root-cause?use_llm=${useLlm}`);
}

export async function fetchAssetRecommendations(assetId: string): Promise<Recommendation[]> {
  const data = await apiGet<RecommendationListResponse>(`/intelligence/assets/${assetId}/recommendations`);
  return data.items.map((item, i) => ({
    id: item.asset_id || String(i),
    asset_id: item.asset_id,
    title: item.title,
    description: item.rationale,
    priority: item.priority,
    hint: item.rationale,
    asset_count: 1,
  }));
}

export function fetchCacheStatus() {
  return apiGet<{ warm: boolean; scored_assets: number }>("/intelligence/cache-status");
}

export function fetchHighRiskAssets(limit = 20) {
  return apiGet<{
    items: Array<{
      asset_id: string;
      asset_tag: string;
      asset_name: string;
      asset_type_name?: string | null;
      health_score: number;
      risk_level: string;
    }>;
    total: number;
  }>(`/intelligence/high-risk?limit=${limit}`);
}

const SCORE_BATCH_TIMEOUT_MS = 180_000;

export function runScoreBatch(persist = true) {
  return apiPost<{ scored: number; failed: number }>(
    `/intelligence/score-batch?persist=${persist}`,
    {},
    SCORE_BATCH_TIMEOUT_MS,
  );
}
