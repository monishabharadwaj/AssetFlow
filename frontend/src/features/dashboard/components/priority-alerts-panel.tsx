import { useMemo } from "react";
import { Link } from "@tanstack/react-router";
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

import { Card, CardHeader, EmptyState, Skeleton } from "@/components/ui-bits";
import { ChartTooltip } from "@/lib/chart-tooltip";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
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
    return [...buckets.entries()].map(([type, value]) => ({
      type,
      name: TYPE_LABELS[type] ?? "Other",
      value,
      color: TYPE_COLORS[type] ?? TYPE_COLORS.OTHER,
    }));
  }, [attentionItems]);

  const total = chartData.reduce((a, b) => a + b.value, 0);
  const hasChart = total > 0;
  const hasMaintenance = (upcomingMaintenance?.length ?? 0) > 0;

  return (
    <Card className={cn(glassCardClass(), "h-full max-h-56")}>
      <CardHeader title="Maintenance & alerts" subtitle="Attention items by category" />
      {loading ? (
        <Skeleton className="h-36" />
      ) : hasChart ? (
        <div className="grid grid-cols-2 gap-2 h-36">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                innerRadius={28}
                outerRadius={44}
                paddingAngle={2}
                stroke="none"
              >
                {chartData.map((d) => (
                  <Cell key={d.type} fill={d.color} />
                ))}
              </Pie>
              <ChartTooltip
                formatter={(value, _name, props) => {
                  const num = Number(value);
                  const label = (props as { payload?: { name: string } }).payload?.name ?? "";
                  const pctVal = total > 0 ? Math.round((num / total) * 100) : 0;
                  return [`${num} (${pctVal}%)`, label];
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <ul className="flex flex-col justify-center gap-1 text-[10px] min-w-0">
            {chartData.map((d) => (
              <li key={d.type} className="flex items-center justify-between gap-1">
                <span className="flex items-center gap-1 text-muted-foreground truncate">
                  <span className="size-2 rounded-full shrink-0" style={{ background: d.color }} />
                  {d.name}
                </span>
                <span className="tabular-nums font-medium text-foreground shrink-0">
                  {d.value}
                  <span className="text-muted-foreground ml-0.5">
                    ({total > 0 ? Math.round((d.value / total) * 100) : 0}%)
                  </span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : hasMaintenance ? (
        <ul className="space-y-1.5 text-xs max-h-36 overflow-y-auto">
          {upcomingMaintenance!.slice(0, 5).map((m, i) => (
            <li key={`${m.asset_id}-${i}`}>
              <Link
                to="/assets/$id"
                params={{ id: m.asset_id }}
                className="flex justify-between gap-2 rounded-md border border-border/80 px-2 py-1.5 hover:bg-accent/30"
              >
                <span className="font-medium truncate">{m.asset_tag}</span>
                <span className="text-muted-foreground shrink-0">
                  {m.scheduled_date ? fmtDate(m.scheduled_date) : "TBD"}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState title="No alerts" hint="Attention items appear after fleet analysis." />
      )}
    </Card>
  );
}
