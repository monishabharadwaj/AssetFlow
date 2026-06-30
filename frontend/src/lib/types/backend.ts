export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type AssetStatus =
  | "AVAILABLE"
  | "ASSIGNED"
  | "IN_MAINTENANCE"
  | "RETIRED"
  | "DISPOSED";

export type UserRole = "ADMIN" | "MANAGER" | "VIEWER";

export interface AuthUser {
  id: string;
  role: UserRole;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
  employee_id: string;
  email: string;
  full_name: string;
  employee_code: string;
  job_title: string | null;
  department_id: string;
  department_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  must_change_password: boolean;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export type DashboardSummaryResponse = {
  total_assets: number;
  total_active_assets: number;
  total_employees: number;
  total_active_employees: number;
  total_departments: number;
  total_active_departments: number;
  assets_by_status: Array<{ status: string; count: number }>;
  assets_by_department: Array<{
    department_id: string;
    department_name: string;
    count: number;
  }>;
  maintenance_due_count: number;
  recent_activity: Array<{
    activity_type: string;
    occurred_at: string;
    asset_id: string;
    asset_tag: string;
    asset_name: string;
    headline: string;
    message: string;
  }>;
  attention_items: Array<{
    priority: string;
    item_type: string;
    asset_id: string;
    asset_tag: string;
    asset_name: string;
    headline: string;
    message: string;
    occurred_at: string | null;
  }>;
  operational_posture?: {
    critical_count: number;
    warning_count: number;
    monitor_count: number;
    healthy_count: number;
    excellent_count: number;
    recently_improved_count: number;
    fleet_health_avg_pct?: number;
    ai_scored_count: number;
    maintenance_completed_today: number;
  };
  health_distribution?: Array<{
    band: string;
    label: string;
    count: number;
  }>;
};

export type Asset = {
  id: string;
  asset_tag: string;
  name: string;
  asset_type_id: string;
  purchase_date: string;
  purchase_cost: string;
  current_status: AssetStatus;
  current_location: string;
  current_department_id: string;
  current_assigned_employee_id: string | null;
  serial_number: string | null;
  manufacturer: string | null;
  model: string | null;
  warranty_expiry: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type AssetSearchParams = {
  page?: number;
  page_size?: number;
  name?: string;
  asset_tag?: string;
  serial_number?: string;
  current_status?: AssetStatus;
  current_department_id?: string;
  current_location?: string;
};

export type Department = {
  id: string;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type Employee = {
  id: string;
  department_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  job_title: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

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
    deteriorating: Array<{ asset_id: string; asset_tag: string; asset_name: string; health_delta: number }>;
    improving_count: number;
    health_trend_chart: ChartPoint[];
    department_comparison: ChartPoint[];
    ai_insight: string;
    key_factors: string[];
  };
  cost: {
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
      priority: string;
      why_replace: string;
      remaining_useful_life_months: number;
      replace_within_months?: number;
      health_score?: number | null;
      life_remaining_pct?: number;
    }>;
    ai_insight: string;
  };
  maintenance: {
    items: Array<{
      asset_id: string;
      asset_tag: string;
      asset_name: string;
      suggested_window: string;
      suggested_within_days: number;
      rationale: string;
    }>;
    priority_ranking: ChartPoint[];
    department_workload: ChartPoint[];
    ai_insight: string;
    skip_risk_summary: string;
  };
  scoring: {
    last_run_at: string | null;
    scored_assets: number;
  };
};

export type MaintenanceRecommendation = {
  asset_id: string;
  asset_tag: string;
  asset_name: string;
  title: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  rationale: string;
};

export type RecommendationListResponse = {
  items: MaintenanceRecommendation[];
  total: number;
};

export type AssetCreate = {
  asset_tag: string;
  name: string;
  asset_type_id: string;
  purchase_date: string;
  purchase_cost: number;
  current_location?: string;
  current_department_id: string;
  serial_number?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  warranty_expiry?: string | null;
};

export type AssetUpdate = Partial<{
  asset_tag: string;
  name: string;
  asset_type_id: string;
  purchase_date: string;
  purchase_cost: number;
  current_status: AssetStatus;
  current_location: string;
  current_department_id: string;
  serial_number: string | null;
  manufacturer: string | null;
  model: string | null;
  warranty_expiry: string | null;
  is_active: boolean;
}>;

export type AssetCategory = {
  id: string;
  name: string;
  description: string | null;
};

export type AssetType = {
  id: string;
  category_id: string;
  name: string;
  description: string | null;
};

export type DepartmentCreate = { name: string; code: string; description?: string | null };
export type DepartmentUpdate = Partial<DepartmentCreate & { is_active: boolean }>;

export type EmployeeCreate = {
  department_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  job_title?: string | null;
};
export type EmployeeUpdate = Partial<EmployeeCreate & { is_active: boolean }>;

export type MaintenanceType = "PREVENTIVE" | "CORRECTIVE" | "INSPECTION" | "UPGRADE" | "OTHER";
export type MaintenanceStatus = "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";

export type Maintenance = {
  id: string;
  asset_id: string;
  maintenance_type: MaintenanceType;
  status: MaintenanceStatus;
  scheduled_date: string | null;
  completed_date: string | null;
  cost: string | null;
  description: string;
  service_provider: string | null;
  created_at: string;
  updated_at: string;
};

export type MaintenanceCreate = {
  maintenance_type: MaintenanceType;
  status?: MaintenanceStatus;
  scheduled_date?: string | null;
  description: string;
  service_provider?: string | null;
};

export type MaintenanceUpdate = Partial<MaintenanceCreate & { completed_date?: string | null; cost?: number | null }>;

export type MaintenanceWorkQueueItem = {
  record: Maintenance;
  asset_id: string;
  asset_tag: string;
  asset_name: string;
};

export type Allocation = {
  id: string;
  asset_id: string;
  employee_id: string;
  action: "ASSIGN" | "RETURN" | "REASSIGN";
  allocated_at: string;
  returned_at: string | null;
  notes: string | null;
};

export type Transfer = {
  id: string;
  asset_id: string;
  from_department_id: string;
  to_department_id: string;
  from_location: string;
  to_location: string;
  transferred_at: string;
  reason: string | null;
};

export type TransferCreate = {
  to_department_id: string;
  to_location: string;
  transferred_at: string;
  reason?: string | null;
};

export type HealthHistory = {
  id: string;
  asset_id: string;
  recorded_at: string;
  health_score: string | null;
  condition_rating: number | null;
  failure_count: number;
  notes: string | null;
};

export type HealthHistoryCreate = {
  health_score?: number | null;
  condition_rating?: number | null;
  notes?: string | null;
};

export type TimelineEvent = {
  event_type: string;
  occurred_at: string;
  title: string;
  details: Record<string, unknown>;
};

export type MyWorkspaceResponse = {
  full_name: string;
  department_name: string;
  role: UserRole;
  assigned_assets: Array<{
    id: string;
    asset_tag: string;
    name: string;
    current_status: string;
    asset_type_name: string | null;
  }>;
  upcoming_maintenance: Array<{
    asset_id: string;
    asset_tag: string;
    maintenance_type: string;
    scheduled_date: string | null;
    status: string;
    description: string | null;
  }>;
  notifications: Array<{
    id: string;
    title: string;
    severity: string;
    message: string;
    asset_id: string | null;
    created_at: string;
  }>;
  department_asset_count: number;
};

export type ExplanationFactor = {
  factor: string;
  severity: string;
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

export type PredictionExplanation = {
  anomaly_detected: boolean;
  health_delta: number | null;
  previous_health_score: number | null;
  factors: ExplanationFactor[];
  summary: string;
  enterprise_brief: EnterpriseHealthBrief | null;
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
  anomaly_detected?: boolean;
  enterprise_brief?: EnterpriseHealthBrief | null;
};

export type HealthPredictionResponse = {
  asset_id: string;
  asset_tag: string | null;
  asset_name: string | null;
  asset_type_name: string | null;
  department_name: string | null;
  health_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  confidence: number;
  model_version: string;
  training_dataset: string;
  features_used: string[];
  prediction_metadata: Record<string, unknown>;
  predicted_at: string;
  explanation: PredictionExplanation | null;
};

/** @deprecated Use HealthPredictionResponse */
export type HealthPrediction = {
  asset_id: string;
  health_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  confidence: number;
};

export type PipelineStatus = {
  scheduler_enabled: boolean;
  scheduler_interval_minutes?: number;
  last_run_at: string | null;
  cache_warm: boolean;
  scored_assets: number;
  policy_automation_enabled?: boolean;
};

export type AssistantChatResponse = {
  answer: string;
  tools_used: string[];
  sources: Array<{ label: string; asset_id: string; url: string }>;
};
