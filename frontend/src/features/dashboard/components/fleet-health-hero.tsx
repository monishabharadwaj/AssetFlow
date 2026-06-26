import { Area, AreaChart, ResponsiveContainer } from "recharts";

import type { DashboardSummary } from "../../../shared/api/types";
import { HealthDistributionDonut } from "../../../shared/components/charts/health-distribution-donut";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { HEALTH_BAND_TEXT, type HealthBand } from "../../../shared/lib/ops-semantics";
import { cn } from "../../../shared/lib/utils";

type FleetHealthHeroProps = {
  summary: DashboardSummary;
};

export function FleetHealthHero({ summary }: FleetHealthHeroProps) {
  const posture = summary.operational_posture;
  const distribution = summary.health_distribution ?? [];
  const totalScored = distribution.reduce((sum, d) => sum + d.count, 0);
  const trend = summary.health_trend_30d ?? [];

  const chips = posture
    ? [
        { label: "Critical", count: posture.critical_count, className: "text-red-400 bg-red-500/10" },
        { label: "Warning", count: posture.warning_count, className: "text-orange-400 bg-orange-500/10" },
        { label: "Monitor", count: posture.monitor_count, className: "text-amber-400 bg-amber-500/10" },
        {
          label: "Healthy",
          count: posture.healthy_count + posture.excellent_count,
          className: "text-emerald-400 bg-emerald-500/10",
        },
        { label: "Improved", count: posture.recently_improved_count, className: "text-sky-400 bg-sky-500/10" },
      ].filter((c) => c.count > 0)
    : [];

  return (
    <Card className="glass-card gradient-hero overflow-hidden border-border/60">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl">Fleet health overview</CardTitle>
        <CardDescription>
          {summary.ops_headline || "Operational snapshot across your asset fleet"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <HealthDistributionDonut
              segments={distribution}
              total={totalScored || summary.total_active_assets}
              centerLabel="Assets scored"
            />
            <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1">
              {distribution.map((band) => (
                <div key={band.band} className="flex items-center gap-1.5 text-xs">
                  <span className={cn("font-medium", HEALTH_BAND_TEXT[band.band as HealthBand])}>
                    {band.label.split(" ")[0]}
                  </span>
                  <span className="text-muted-foreground">({band.count})</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4 lg:col-span-4">
            {posture?.fleet_health_avg_pct != null ? (
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Average AI score
                </p>
                <p className="text-4xl font-semibold tabular-nums text-primary">
                  {posture.fleet_health_avg_pct}%
                </p>
              </div>
            ) : null}
            {chips.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {chips.map((chip) => (
                  <span
                    key={chip.label}
                    className={cn("rounded-full px-3 py-1 text-xs font-medium", chip.className)}
                  >
                    {chip.label}: {chip.count}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Run the AI pipeline to populate fleet health distribution.
              </p>
            )}
            {posture ? (
              <div className="grid grid-cols-2 gap-2 text-sm">
                <Stat label="Maint. done today" value={posture.maintenance_completed_today} />
                <Stat label="AI scored" value={posture.ai_scored_count} />
              </div>
            ) : null}
          </div>

          <div className="hidden items-center justify-center lg:col-span-3 lg:flex">
            <svg viewBox="0 0 120 120" className="ai-core-glow h-28 w-28" aria-hidden>
              <defs>
                <linearGradient id="aiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="hsl(230,63%,58%)" />
                  <stop offset="100%" stopColor="hsl(190,90%,50%)" />
                </linearGradient>
              </defs>
              <polygon points="60,15 95,45 80,95 40,95 25,45" fill="url(#aiGrad)" opacity="0.85" />
              <polygon points="60,30 82,50 72,82 48,82 38,50" fill="hsl(224,28%,8%)" opacity="0.6" />
            </svg>
          </div>
        </div>

        {trend.length > 1 ? (
          <div className="mt-6 border-t border-border/40 pt-4">
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Health trend — 30 days
            </p>
            <div className="h-16 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trend}>
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(230,63%,58%)"
                    fill="hsl(230,63%,58%)"
                    fillOpacity={0.15}
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-border/50 bg-background/40 px-3 py-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}
