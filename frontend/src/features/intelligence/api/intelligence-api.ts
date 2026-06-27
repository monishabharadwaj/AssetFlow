import { apiGet, apiPost } from "../../../shared/api/client";

export type HealthPrediction = {
  asset_id: string;
  asset_tag: string | null;
  asset_name: string | null;
  health_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  confidence: number;
  model_version: string;
  training_dataset: string;
  features_used: string[];
  prediction_metadata: Record<string, unknown>;
  predicted_at: string;
};

export type MaintenanceRecommendation = {
  asset_id: string;
  asset_tag: string;
  asset_name: string;
  title: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  maintenance_type: string;
  suggested_within_days: number;
  rationale: string;
  risk_level: string;
  predicted_health_score: number;
};

export function predictAssetHealth(assetId: string, persist = false) {
  return apiPost<HealthPrediction>(`/intelligence/assets/${assetId}/predict?persist=${persist}`, {});
}

export function scoreBatch(persist = false) {
  return apiPost<{ scored: number; failed: number; results: HealthPrediction[] }>(
    `/intelligence/score-batch?persist=${persist}`,
    {},
  );
}

export function fetchHighRiskAssets(limit = 20) {
  return apiGet<{ items: HealthPrediction[]; total: number }>(
    `/intelligence/high-risk?limit=${limit}`,
  );
}

export function fetchRecommendations(limit = 10) {
  return apiGet<{ items: MaintenanceRecommendation[]; total: number }>(
    `/intelligence/recommendations?limit=${limit}`,
  );
}

export function fetchPredictionCacheStatus() {
  return apiGet<{ warm: boolean; scored_assets: number }>("/intelligence/cache-status");
}

export function fetchAssetRecommendations(assetId: string, limit = 5) {
  return apiGet<{ items: MaintenanceRecommendation[]; total: number }>(
    `/intelligence/assets/${assetId}/recommendations?limit=${limit}`,
  );
}

export type AssistantChatResponse = {
  answer: string;
  tools_used: string[];
  sources: Array<{ label: string; asset_id: string; url: string }>;
};

export type ChatHistoryItem = {
  role: "user" | "assistant";
  content: string;
};

export function assistantChat(data: { message: string; history: ChatHistoryItem[] }) {
  return apiPost<AssistantChatResponse>("/assistant/chat", data);
}

export type MaintenanceWorkQueueItem = {
  record: {
    id: string;
    asset_id: string;
    maintenance_type: string;
    status: string;
    scheduled_date: string | null;
    description: string;
  };
  asset_id: string;
  asset_tag: string;
  asset_name: string;
};

export function fetchMaintenanceWorkQueue(page = 1, pageSize = 20) {
  return apiGet<{
    items: MaintenanceWorkQueueItem[];
    total: number;
    page: number;
    pages: number;
  }>(`/maintenance?page=${page}&page_size=${pageSize}`);
}

export type ExplanationFactor = {
  factor: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  message: string;
};

export type EnterpriseHealthBrief = {
  what_happened: string;
  why_predicted: string;
  business_impact: string;
  recommended_action: string;
  priority: string;
  estimated_downtime: string;
  estimated_effort: string;
  estimated_cost: string | null;
  health_band: string;
  confidence_label: string;
  remaining_useful_life: string | null;
  is_improvement: boolean;
};

export type RootCauseResponse = {
  asset_id: string;
  asset_tag: string | null;
  asset_name: string | null;
  health_score: number;
  risk_level: string;
  root_cause_summary: string;
  source: string;
  factors: ExplanationFactor[];
  anomaly_detected: boolean;
  enterprise_brief: EnterpriseHealthBrief | null;
};

export function fetchAssetRootCause(assetId: string, useLlm = true) {
  return apiGet<RootCauseResponse>(`/intelligence/assets/${assetId}/root-cause?use_llm=${useLlm}`);
}

