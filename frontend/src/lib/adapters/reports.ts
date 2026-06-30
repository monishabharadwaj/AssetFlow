import type { ReportsAnalytics } from "@/lib/types/backend";
import type { OperationsReport, Priority } from "@/lib/types/ui";
import { formatCurrency, formatReplaceWindow } from "@/lib/format";

export function mapReportsAnalytics(data: ReportsAnalytics, enhanced: boolean): OperationsReport {
  const savings = Number(data.kpis.estimated_annual_savings ?? data.cost.estimated_annual_savings ?? 0);
  const metrics = [
    { label: "Active assets", value: data.kpis.active_assets ?? "—" },
    { label: "Avg fleet health", value: `${data.kpis.avg_fleet_health_pct ?? "—"}%` },
    { label: "High risk", value: data.kpis.high_risk_assets ?? "—" },
    { label: "Maintenance due", value: data.kpis.maintenance_due ?? "—" },
    { label: "Drift alerts", value: data.kpis.drift_alerts ?? "—" },
    { label: "Est. savings", value: formatCurrency(savings) },
  ];

  if (data.benchmarks) {
    metrics.push(
      { label: "Company avg health", value: `${data.benchmarks.org_avg_fleet_health_pct}%` },
      {
        label: "Dept vs company",
        value: `${data.benchmarks.dept_vs_org_health_delta >= 0 ? "+" : ""}${data.benchmarks.dept_vs_org_health_delta}%`,
      },
      { label: "Company high-risk", value: data.benchmarks.org_high_risk_assets },
    );
  }

  const sections = data.executive_sections.map((s, i) => ({
    number: i + 1,
    title: s.title,
    paragraphs: [s.summary],
    bullets: s.bullets,
  }));

  const report: OperationsReport = {
    scope: data.scope_label,
    generated_at: data.generated_at,
    metrics,
    sections,
    source: data.source,
    ollama_enabled: data.ollama_enabled,
    enhanced,
    text_summaries: {
      drift: data.drift.ai_insight,
      cost: data.cost.ai_insight,
      replacement: data.replacement.ai_insight,
      maintenance: data.maintenance.ai_insight,
    },
    standard_charts: {
      health_trend_chart: data.drift.health_trend_chart,
      priority_ranking: data.maintenance.priority_ranking,
      department_workload: data.maintenance.department_workload,
      department_comparison: data.drift.department_comparison,
    },
  };

  if (enhanced) {
    report.appendices = {
      benchmarks: data.benchmarks
        ? [
            {
              label: "Company avg health",
              value: data.benchmarks.org_avg_fleet_health_pct,
            },
            {
              label: "Dept vs company avg",
              value: data.benchmarks.dept_vs_org_health_delta,
              company_avg: 0,
            },
            {
              label: "Company high-risk",
              value: data.benchmarks.org_high_risk_assets,
            },
          ]
        : undefined,
      health_drift: data.drift.health_trend_chart.map((p) => ({
        name: p.label,
        current: p.value,
        previous: Math.max(0, p.value - 5),
      })),
      cost_optimization: data.cost.cost_distribution.map((p) => ({
        name: p.label,
        savings: p.value,
      })),
      replacement_planning: data.replacement.items.map((item) => {
        const months = item.replace_within_months ?? item.remaining_useful_life_months;
        return {
          asset_tag: item.asset_tag,
          name: item.asset_name,
          priority: item.priority as Priority,
          healthPct: item.health_score != null ? Math.round(item.health_score * 100) : null,
          lifeRemainingPct: item.life_remaining_pct ?? 0,
          replaceWithinMonths: months,
          recommendedWindow: formatReplaceWindow(months, data.generated_at),
          reason: item.why_replace,
        };
      }),
      maintenance_schedule: data.maintenance.items.map((item) => ({
        asset_tag: item.asset_tag,
        name: item.asset_name,
        dueWindow: item.suggested_window,
        dueDays: item.suggested_within_days,
        priority: (item.suggested_within_days <= 7 ? "HIGH" : item.suggested_within_days <= 30 ? "MEDIUM" : "LOW") as Priority,
      })),
      health_trend_chart: data.drift.health_trend_chart,
      department_comparison: data.drift.department_comparison,
      priority_ranking: data.maintenance.priority_ranking,
      department_workload: data.maintenance.department_workload,
    };
  }

  return report;
}
