import type { DashboardSummaryResponse } from "@/lib/types/backend";
import type { DashboardSummary } from "@/lib/types/ui";

function mapPriority(priority: string): "Critical" | "High" | "Medium" | "Low" {
  const p = priority.toUpperCase();
  if (p === "CRITICAL" || p === "HIGH") return p === "CRITICAL" ? "Critical" : "High";
  if (p === "MEDIUM") return "Medium";
  return "Low";
}

function mapHealthDistribution(data: DashboardSummaryResponse): DashboardSummary["health_distribution"] {
  if (data.health_distribution?.length) {
    const bands = { healthy: 0, monitor: 0, warning: 0, critical: 0 };
    for (const item of data.health_distribution) {
      const key = item.band.toLowerCase();
      if (key.includes("critical")) bands.critical += item.count;
      else if (key.includes("warning")) bands.warning += item.count;
      else if (key.includes("monitor")) bands.monitor += item.count;
      else bands.healthy += item.count;
    }
    return bands;
  }
  const op = data.operational_posture;
  if (op) {
    return {
      healthy: (op.healthy_count ?? 0) + (op.excellent_count ?? 0),
      monitor: op.monitor_count ?? 0,
      warning: op.warning_count ?? 0,
      critical: op.critical_count ?? 0,
    };
  }
  return { healthy: 0, monitor: 0, warning: 0, critical: 0 };
}

export function mapDashboardSummary(data: DashboardSummaryResponse): DashboardSummary {
  const status_distribution: Record<string, number> = {};
  for (const item of data.assets_by_status) {
    status_distribution[item.status] = item.count;
  }

  const avgHealthPct = data.operational_posture?.fleet_health_avg_pct;
  const avg_health = avgHealthPct != null ? avgHealthPct / 100 : undefined;

  return {
    scope: data.total_departments > 1 ? "organization" : "department",
    kpis: {
      total_assets: data.total_active_assets,
      employees: data.total_active_employees,
      departments: data.total_active_departments,
      maintenance_due: data.maintenance_due_count,
      avg_health,
    },
    health_distribution: mapHealthDistribution(data),
    status_distribution,
    department_distribution: data.assets_by_department.map((d) => ({
      name: d.department_name,
      count: d.count,
    })),
    attention_items: data.attention_items.map((item, i) => ({
      id: `${item.asset_id}-${i}`,
      title: item.headline || item.message,
      subtitle: item.asset_tag ? `${item.asset_tag} · ${item.asset_name}` : item.message,
      severity: mapPriority(item.priority),
      asset_id: item.asset_id,
      asset_tag: item.asset_tag,
      asset_name: item.asset_name,
      item_type: item.item_type,
    })),
    recent_activity: data.recent_activity.map((item, i) => ({
      id: `${item.asset_id}-${item.occurred_at}-${i}`,
      title: item.headline || item.activity_type,
      subtitle: item.message,
      timestamp: item.occurred_at,
      asset_id: item.asset_id,
      activity_type: item.activity_type,
    })),
    trend_text: undefined,
  };
}
