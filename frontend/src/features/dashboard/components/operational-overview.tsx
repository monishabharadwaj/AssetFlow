import { Link } from "react-router-dom";

import type { DashboardSummary } from "../../../shared/api/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { HEALTH_BAND_COLORS, HEALTH_BAND_TEXT, type HealthBand } from "../../../shared/lib/ops-semantics";
import { cn } from "../../../shared/lib/utils";

type OperationalOverviewProps = {
  summary: DashboardSummary;
};

export function OperationalOverview({ summary }: OperationalOverviewProps) {
  const posture = summary.operational_posture;
  const distribution = summary.health_distribution ?? [];
  const totalScored = distribution.reduce((sum, d) => sum + d.count, 0);

  const postureChips = posture
    ? [
        { label: "Critical", count: posture.critical_count, className: "bg-red-100 text-red-800" },
        { label: "Warning", count: posture.warning_count, className: "bg-orange-100 text-orange-800" },
        { label: "Monitor", count: posture.monitor_count, className: "bg-amber-100 text-amber-800" },
        {
          label: "Healthy",
          count: posture.healthy_count + posture.excellent_count,
          className: "bg-emerald-100 text-emerald-800",
        },
        { label: "Improved", count: posture.recently_improved_count, className: "bg-sky-100 text-sky-800" },
        {
          label: "Maint. done today",
          count: posture.maintenance_completed_today,
          className: "bg-slate-100 text-slate-700",
        },
      ].filter((c) => c.count > 0)
    : [];

  return (
    <Card className="border-primary/10">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Fleet health overview</CardTitle>
        <CardDescription>{summary.ops_headline || "Operational snapshot across your asset fleet."}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {postureChips.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {postureChips.map((chip) => (
              <span
                key={chip.label}
                className={cn("rounded-full px-3 py-1 text-xs font-medium", chip.className)}
              >
                {chip.label}: {chip.count}
              </span>
            ))}
            {posture?.fleet_health_avg_pct != null ? (
              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-800">
                Fleet avg: {posture.fleet_health_avg_pct}%
              </span>
            ) : null}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Run the AI pipeline to populate fleet health distribution.
          </p>
        )}

        {totalScored > 0 ? (
          <div className="space-y-2">
            <div className="flex h-3 overflow-hidden rounded-full bg-muted">
              {distribution.map((band) => {
                if (band.count === 0) return null;
                const width = (band.count / totalScored) * 100;
                return (
                  <div
                    key={band.band}
                    className={cn("h-full transition-all", HEALTH_BAND_COLORS[band.band as HealthBand])}
                    style={{ width: `${width}%` }}
                    title={`${band.label}: ${band.count}`}
                  />
                );
              })}
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1">
              {distribution.map((band) => (
                <div key={band.band} className="flex items-center gap-1.5 text-xs">
                  <span
                    className={cn("h-2 w-2 rounded-full", HEALTH_BAND_COLORS[band.band as HealthBand])}
                  />
                  <span className={HEALTH_BAND_TEXT[band.band as HealthBand]}>{band.label}</span>
                  <span className="text-muted-foreground">({band.count})</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <MetricLink label="Assets" value={summary.total_active_assets} href="/assets" />
          <MetricLink
            label="Maint. due"
            value={summary.maintenance_due_count}
            href="/maintenance"
            highlight={summary.maintenance_due_count > 0}
          />
          <MetricLink label="AI scored" value={posture?.ai_scored_count ?? 0} href="/dashboard" />
          <MetricLink
            label="Critical"
            value={posture?.critical_count ?? 0}
            href="/dashboard"
            critical
            highlight={(posture?.critical_count ?? 0) > 0}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function MetricLink({
  label,
  value,
  href,
  highlight,
  critical,
}: {
  label: string;
  value: number;
  href: string;
  highlight?: boolean;
  critical?: boolean;
}) {
  return (
    <Link
      to={href}
      className={cn(
        "rounded-lg border px-3 py-2 transition-shadow hover:shadow-sm",
        critical && value > 0
          ? "border-red-200 bg-red-50/30"
          : highlight
            ? "border-amber-200 bg-amber-50/20"
            : "bg-card",
      )}
    >
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className={cn("text-xl font-semibold tracking-tight", critical && value > 0 && "text-red-700")}>
        {value.toLocaleString()}
      </p>
    </Link>
  );
}
