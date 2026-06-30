import type { AssetStatus } from "./backend";

export type Role = "ADMIN" | "MANAGER" | "VIEWER";

export type HealthBand = "Healthy" | "Monitor" | "Warning" | "Critical";

export type RiskLevel = "HIGH" | "MEDIUM" | "LOW";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  department_id?: string | null;
  department_name?: string | null;
  must_change_password?: boolean;
  job_title?: string | null;
  employee_code?: string | null;
}

export type Priority = "HIGH" | "MEDIUM" | "LOW";

export interface AssetListItem {
  id: string;
  asset_tag: string;
  name: string;
  status: AssetStatus;
  department_id: string;
  department_name?: string | null;
  location: string;
  serial_number?: string | null;
  health_score?: number | null;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page?: number;
  page_size?: number;
}

export interface AttentionItem {
  id: string;
  title: string;
  subtitle?: string | null;
  severity: "Critical" | "High" | "Medium" | "Low";
  asset_id?: string | null;
  asset_tag?: string | null;
  asset_name?: string | null;
  item_type?: string | null;
}

export interface ActivityItem {
  id: string;
  title: string;
  subtitle?: string | null;
  timestamp: string;
  asset_id?: string | null;
  activity_type?: string | null;
}

export interface DashboardSummary {
  scope: "organization" | "department";
  scope_label?: string;
  kpis: {
    total_assets: number;
    employees: number;
    departments?: number;
    maintenance_due: number;
    avg_health?: number;
    deltas?: Record<string, string | number>;
  };
  health_distribution: { healthy: number; monitor: number; warning: number; critical: number };
  status_distribution?: Record<string, number>;
  department_distribution?: { name: string; count: number }[];
  attention_items: AttentionItem[];
  recent_activity: ActivityItem[];
  trend_text?: string;
}

export interface Recommendation {
  id: string;
  asset_id?: string | null;
  title: string;
  description?: string;
  priority: Priority;
  category?: string;
  asset_count?: number;
  hint?: string;
}

export interface Notification {
  id: string;
  title: string;
  body?: string;
  read: boolean;
  created_at: string;
  severity?: "info" | "warning" | "critical";
  asset_id?: string | null;
}

export interface ReportSection {
  number?: number;
  title: string;
  paragraphs?: string[];
  bullets?: string[];
}

export interface ReportMetric {
  label: string;
  value: string | number;
}

export interface OperationsReport {
  scope: string;
  generated_at: string;
  metrics: ReportMetric[];
  sections: ReportSection[];
  source?: string;
  ollama_enabled?: boolean;
  enhanced?: boolean;
  text_summaries?: {
    drift?: string;
    cost?: string;
    replacement?: string;
    maintenance?: string;
  };
  appendices?: {
    health_drift?: { name: string; current: number; previous: number }[];
    cost_optimization?: { name: string; savings: number }[];
    replacement_planning?: {
      asset_tag: string;
      name: string;
      priority: Priority;
      healthPct: number | null;
      lifeRemainingPct: number;
      replaceWithinMonths: number;
      recommendedWindow: string;
      reason?: string;
    }[];
    maintenance_schedule?: { asset_tag: string; name: string; dueWindow: string; dueDays?: number; priority: Priority }[];
    benchmarks?: { label: string; value: number; company_avg?: number }[];
    health_trend_chart?: { label: string; value: number }[];
    department_comparison?: { label: string; value: number }[];
    priority_ranking?: { label: string; value: number }[];
    department_workload?: { label: string; value: number }[];
  };
  /** Chart data available in standard report (no enhanced toggle required). */
  standard_charts?: {
    health_trend_chart?: { label: string; value: number }[];
    priority_ranking?: { label: string; value: number }[];
    department_workload?: { label: string; value: number }[];
    department_comparison?: { label: string; value: number }[];
  };
}
