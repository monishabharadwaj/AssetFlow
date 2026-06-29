import { apiGet, apiPatch, apiPost } from "../../../shared/api/client";

export type NotificationItem = {
  id: string;
  notification_type: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  title: string;
  message: string;
  asset_id: string | null;
  is_read: boolean;
  created_at: string;
};

export type PipelineStatus = {
  scheduler_enabled: boolean;
  scheduler_interval_minutes: number;
  last_run_at: string | null;
  cache_warm: boolean;
  scored_assets: number;
  policy_automation_enabled: boolean;
};

export type PipelineRunResult = {
  scored: number;
  failed: number;
  notifications_created: number;
  maintenance_auto_scheduled: number;
  drift_alerts: number;
  ran_at: string;
};

export type DriftAlert = {
  asset_id: string;
  asset_tag: string;
  asset_name: string;
  previous_health?: number;
  current_health?: number;
  health_delta: number;
  message: string;
};

export type OperationalReport = {
  title: string;
  generated_at: string;
  summary: string;
  sections: string[];
  source: string;
  metrics: Record<string, number | string>;
};

export function fetchNotifications(limit = 20, unreadOnly = false) {
  return apiGet<{ items: NotificationItem[]; total: number; unread_count: number }>(
    `/operations/notifications?limit=${limit}&unread_only=${unreadOnly}`,
  );
}

export function markNotificationRead(id: string) {
  return apiPatch<NotificationItem>(`/operations/notifications/${id}/read`, {});
}

export function markAllNotificationsRead() {
  return apiPost<{ marked_read: number }>("/operations/notifications/read-all", {});
}

export function fetchPipelineStatus() {
  return apiGet<PipelineStatus>("/operations/pipeline/status");
}

export function runPipeline(persist = true) {
  return apiPost<PipelineRunResult>(`/operations/pipeline/run?persist=${persist}`, {});
}

export function fetchWeeklyReport(useLlm = false) {
  return apiGet<OperationalReport>(`/operations/reports/weekly?use_llm=${useLlm}`);
}

export function fetchReplacementPlan(limit = 10) {
  return apiGet<{ items: Array<{
    asset_id: string;
    asset_tag: string;
    asset_name: string;
    asset_type: string;
    health_score: number | null;
    replace_within_months: number;
    rationale: string;
    priority: string;
  }>; total: number }>(`/operations/replacement-plan?limit=${limit}`);
}

export function fetchCostOptimization(limit = 10) {
  return apiGet<{ items: Array<{
    asset_id: string;
    asset_tag: string;
    asset_name: string;
    purchase_cost: number;
    maintenance_spend: number;
    tco_ratio: number;
    recommendation: string;
    priority: string;
  }>; total: number }>(`/operations/cost-optimization?limit=${limit}`);
}

export function fetchMaintenanceSchedule(limit = 10) {
  return apiGet<{ items: Array<{
    asset_id: string;
    asset_tag: string;
    asset_name: string;
    utilization_rate: number;
    suggested_window: string;
    suggested_within_days: number;
    rationale: string;
  }>; total: number }>(`/operations/maintenance-schedule?limit=${limit}`);
}

export function fetchDriftStatus() {
  return apiGet<{ alerts: DriftAlert[]; total: number }>("/operations/drift");
}

export type ChartPoint = { label: string; value: number; category?: string | null };

export type ReportInsightSection = {
  key: string;
  title: string;
  summary: string;
  bullets: string[];
};

export type OrgBenchmarks = {
  org_avg_fleet_health_pct: number;
  dept_vs_org_health_delta: number;
  org_high_risk_assets: number;
};

export type ReportsAnalytics = {
  generated_at: string;
  scope_label: string;
  use_ai: boolean;
  source: string;
  ollama_enabled: boolean;
  benchmarks: OrgBenchmarks | null;
  kpis: Record<string, number | string>;
  executive_sections: ReportInsightSection[];
  drift: {
    alerts: DriftAlert[];
    deteriorating: DriftAlert[];
    improving_count: number;
    health_trend_chart: ChartPoint[];
    department_comparison: ChartPoint[];
    ai_insight: string;
    key_factors: string[];
  };
  cost: {
    items: Array<{
      asset_id: string;
      asset_tag: string;
      asset_name: string;
      purchase_cost: number;
      maintenance_spend: number;
      tco_ratio: number;
      recommendation: string;
      priority: string;
    }>;
    cost_distribution: ChartPoint[];
    department_costs: ChartPoint[];
    estimated_annual_savings: number;
    ai_insight: string;
    opportunities: string[];
  };
  replacement: {
    items: Array<{
      asset_id: string;
      asset_tag: string;
      asset_name: string;
      asset_type: string;
      health_score: number | null;
      age_days: number;
      life_remaining_pct: number;
      replace_within_months: number;
      rationale: string;
      priority: string;
      why_replace: string;
      remaining_useful_life_months: number;
      health_trend: string;
      maintenance_spend: number;
      repair_vs_replace: string;
      business_impact_if_delayed: string;
    }>;
    ai_insight: string;
  };
  maintenance: {
    items: Array<{
      asset_id: string;
      asset_tag: string;
      asset_name: string;
      utilization_rate: number;
      suggested_window: string;
      suggested_within_days: number;
      rationale: string;
    }>;
    priority_ranking: ChartPoint[];
    department_workload: ChartPoint[];
    ai_insight: string;
    skip_risk_summary: string;
  };
  scoring: PipelineStatus;
};

export function fetchReportsAnalytics(useAi = false) {
  const timeoutMs = useAi ? 120_000 : 45_000;
  return apiGet<ReportsAnalytics>(`/operations/reports/analytics?use_ai=${useAi}`, timeoutMs);
}
