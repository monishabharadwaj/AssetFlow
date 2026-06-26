import { AlertTriangle, Box, Sparkles, Wrench } from "lucide-react";

import type { DashboardSummary } from "../../../shared/api/types";
import { PremiumKpiCard } from "./premium-kpi-card";

type KpiHeroRowProps = {
  summary: DashboardSummary;
};

const ICONS: Record<string, typeof Box> = {
  total_assets: Box,
  healthy: Sparkles,
  needs_attention: AlertTriangle,
  critical: AlertTriangle,
  maintenance_due: Wrench,
  ai_score: Sparkles,
};

const HREFS: Record<string, string> = {
  total_assets: "/assets",
  healthy: "/assets",
  needs_attention: "/dashboard",
  critical: "/dashboard",
  maintenance_due: "/maintenance",
  ai_score: "/dashboard",
};

export function KpiHeroRow({ summary }: KpiHeroRowProps) {
  const metrics = summary.kpi_hero?.length ? summary.kpi_hero : buildFallback(summary);

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
      {metrics.map((m) => (
        <PremiumKpiCard
          key={m.key}
          title={m.label}
          value={m.value}
          subtitle={m.delta_label}
          accent={m.accent}
          icon={ICONS[m.key]}
          href={HREFS[m.key]}
          trend={m.trend}
        />
      ))}
    </div>
  );
}

function buildFallback(summary: DashboardSummary) {
  const p = summary.operational_posture;
  const healthy = (p?.excellent_count ?? 0) + (p?.healthy_count ?? 0);
  return [
    { key: "total_assets", label: "Total Assets", value: summary.total_active_assets, accent: "blue", delta_label: null, trend: [] },
    { key: "healthy", label: "Healthy Assets", value: healthy, accent: "green", delta_label: null, trend: [] },
    {
      key: "needs_attention",
      label: "Needs Attention",
      value: (p?.critical_count ?? 0) + (p?.warning_count ?? 0) + summary.maintenance_due_count,
      accent: "amber",
      delta_label: null,
      trend: [],
    },
    { key: "critical", label: "Critical Assets", value: p?.critical_count ?? 0, accent: "red", delta_label: null, trend: [] },
    { key: "maintenance_due", label: "Maintenance Due", value: summary.maintenance_due_count, accent: "purple", delta_label: null, trend: [] },
    { key: "ai_score", label: "AI Score (Avg)", value: p?.fleet_health_avg_pct ?? 0, accent: "cyan", delta_label: null, trend: [] },
  ];
}
