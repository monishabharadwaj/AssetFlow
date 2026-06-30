import { useMemo } from "react";
import { Link } from "@tanstack/react-router";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardHeader, EmptyState, Skeleton } from "@/components/ui-bits";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { chartTooltipStyle } from "@/lib/chart-theme";
import { fmtDate } from "@/lib/format";
import type { AttentionItem } from "@/lib/types/ui";
import { cn } from "@/lib/utils";

type MaintenanceItem = {
  asset_id: string;
  asset_tag: string;
  maintenance_type: string;
  scheduled_date: string | null;
};

const TYPE_LABELS: Record<string, string> = {
  HIGH_RISK: "Asset health",
  MAINTENANCE_DUE: "Maintenance due",
  IN_MAINTENANCE: "In service",
  AVAILABLE_ASSIGNABLE: "Available",
};

const TYPE_COLORS: Record<string, string> = {
  HIGH_RISK: "oklch(0.78 0.22 18)",
  MAINTENANCE_DUE: "oklch(0.85 0.15 75)",
  IN_MAINTENANCE: "oklch(0.7 0.16 240)",
  AVAILABLE_ASSIGNABLE: "oklch(0.72 0.17 155)",
  OTHER: "oklch(0.55 0.02 270)",
};

export function PriorityAlertsPanel({
  attentionItems,
  upcomingMaintenance,
  loading,
}: {
  attentionItems: AttentionItem[];
  upcomingMaintenance?: MaintenanceItem[];
  loading?: boolean;
}) {
  const chartData = useMemo(() => {
    const buckets = new Map<string, number>();
    for (const item of attentionItems) {
      const key = TYPE_LABELS[item.item_type ?? ""] ? (item.item_type ?? "OTHER") : "OTHER";
      buckets.set(key, (buckets.get(key) ?? 0) + 1);
    }
    return [...buckets.entries()]
      .map(([type, value]) => ({
        type,
        name: TYPE_LABELS[type] ?? "Other",
        value,
        color: TYPE_COLORS[type] ?? TYPE_COLORS.OTHER,
      }))
      .sort((a, b) => b.value - a.value);
  }, [attentionItems]);

  const total = chartData.reduce((a, b) => a + b.value, 0);
  const hasAttention = total > 0;
  const hasMaintenance = (upcomingMaintenance?.length ?? 0) > 0;
  const singleCategory = chartData.length === 1;

  return (
    <Card className={cn(glassCardClass(), "h-full max-h-72 overflow-hidden flex flex-col")}>
      <CardHeader
        title="Maintenance & alerts"
        subtitle="Items needing action from AI scoring and maintenance queue"
      />
      {loading ? (
        <Skeleton className="h-44 flex-1" />
      ) : !hasAttention && !hasMaintenance ? (
        <EmptyState title="No alerts" hint="Attention items appear after fleet analysis." />
      ) : (
        <div className="flex flex-col gap-2 flex-1 min-h-0">
          {hasAttention && singleCategory ? (
            <div className="rounded-lg border border-border/80 bg-muted/20 px-3 py-2.5">
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Attention queue</div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-3xl font-semibold tabular-nums">{chartData[0].value}</span>
                <span className="text-sm text-muted-foreground">{chartData[0].name}</span>
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">
                {total === 1
                  ? "One item flagged for follow-up."
                  : `${total} items — all in the same category (${chartData[0].name.toLowerCase()}).`}
              </p>
            </div>
          ) : hasAttention ? (
            <div className="h-28 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ left: 4, right: 8 }}>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" tick={{ fill: "rgb(160,160,180)", fontSize: 9 }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={72}
                    tick={{ fill: "rgb(160,160,180)", fontSize: 9 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={14}>
                    {chartData.map((d) => (
                      <Cell key={d.type} fill={d.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : null}

          {hasMaintenance && (
            <div className={cn("min-h-0", hasAttention ? "border-t border-border/60 pt-2" : "")}>
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">Upcoming</div>
              <ul className="space-y-1 text-xs max-h-20 overflow-y-auto">
                {upcomingMaintenance!.slice(0, 3).map((m, i) => (
                  <li key={`${m.asset_id}-${i}`}>
                    <Link
                      to="/assets/$id"
                      params={{ id: m.asset_id }}
                      className="flex justify-between gap-2 rounded-md border border-border/80 px-2 py-1 hover:bg-accent/30"
                    >
                      <span className="font-medium truncate">{m.asset_tag}</span>
                      <span className="text-muted-foreground shrink-0">
                        {m.scheduled_date ? fmtDate(m.scheduled_date) : "TBD"}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
