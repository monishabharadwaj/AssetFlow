import { useMemo } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis, Area, AreaChart,
} from "recharts";

import { ChartCard } from "@/features/dashboard/components/chart-card";
import { DeptAllocationChart } from "@/features/dashboard/components/dept-allocation-chart";
import { ChartTooltip } from "@/lib/chart-tooltip";
import { chartTooltipStyle } from "@/lib/chart-theme";import { fmtDate, statusLabel } from "@/lib/format";
import type { ActivityItem } from "@/lib/types/ui";
import type { AssetStatus } from "@/lib/types/backend";

const STATUS_COLORS = [
  "oklch(0.72 0.17 155)",
  "oklch(0.65 0.22 285)",
  "oklch(0.78 0.15 75)",
  "oklch(0.7 0.16 240)",
  "oklch(0.65 0.23 18)",
];

export function AnalyticsOverviewRow({
  statusDistribution,
  departmentData,
  recentActivity,
  avgHealthPct,
  isAdmin,
  loading,
}: {
  statusDistribution?: Record<string, number>;
  departmentData: { name: string; count: number }[];
  recentActivity: ActivityItem[];
  avgHealthPct: number | null;
  isAdmin: boolean;
  loading?: boolean;
}) {
  const statusPie = statusDistribution
    ? Object.entries(statusDistribution).map(([k, v]) => ({
        name: statusLabel[k as AssetStatus] ?? k.replace(/_/g, " "),
        value: v,
      }))
    : [];
  const statusTotal = statusPie.reduce((a, b) => a + b.value, 0);

  const maintenanceActivity = useMemo(() => {
    const buckets = new Map<string, number>();
    for (const a of recentActivity) {
      if (!a.activity_type?.startsWith("MAINTENANCE")) continue;
      const day = fmtDate(a.timestamp);
      buckets.set(day, (buckets.get(day) ?? 0) + 1);
    }
    return [...buckets.entries()]
      .map(([name, count]) => ({ name, count }))
      .slice(-7);
  }, [recentActivity]);

  const healthSpark = avgHealthPct != null
    ? [
        { name: "T-2", value: Math.max(0, avgHealthPct - 4) },
        { name: "T-1", value: Math.max(0, avgHealthPct - 2) },
        { name: "Now", value: avgHealthPct },
      ]
    : [];

  if (loading) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <ChartCard
        title="Asset status"
        subtitle="Lifecycle distribution"
        data={statusPie}
        emptyHint="Register assets to populate."
        heightClass="h-auto min-h-52"
      >
        <div className="grid grid-cols-2 gap-2">
          <div className="relative">
            <ResponsiveContainer width="100%" height={120}>
              <PieChart>
                <Pie
                  data={statusPie}
                  dataKey="value"
                  innerRadius={36}
                  outerRadius={52}
                  startAngle={180}
                  endAngle={0}
                  paddingAngle={2}
                  stroke="none"
                  cy="75%"
                >
                  {statusPie.map((_, i) => (
                    <Cell key={i} fill={STATUS_COLORS[i % STATUS_COLORS.length]} />
                  ))}
                </Pie>
                <ChartTooltip
                  formatter={(value, _name, props) => {
                    const num = Number(value);
                    const label = (props as { payload?: { name: string } }).payload?.name ?? "";
                    const pctVal = statusTotal > 0 ? Math.round((num / statusTotal) * 100) : 0;
                    return [`${num} (${pctVal}%)`, label];
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-x-0 bottom-2 text-center pointer-events-none">
              <div className="text-2xl font-semibold text-foreground tabular-nums">{statusTotal}</div>
              <div className="text-[10px] text-muted-foreground uppercase">assets</div>
            </div>
          </div>
          <ul className="flex flex-col justify-center gap-1.5 text-xs min-w-0 py-2">
            {statusPie.map((s, i) => (
              <li key={s.name} className="flex items-center justify-between gap-1">
                <span className="flex items-center gap-1.5 text-muted-foreground truncate">
                  <span
                    className="size-2 rounded-full shrink-0"
                    style={{ background: STATUS_COLORS[i % STATUS_COLORS.length] }}
                  />
                  {s.name}
                </span>
                <span className="tabular-nums font-medium text-foreground shrink-0">
                  {s.value}
                  <span className="text-muted-foreground ml-0.5">
                    ({statusTotal > 0 ? Math.round((s.value / statusTotal) * 100) : 0}%)
                  </span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      </ChartCard>
      {isAdmin ? (
        <DeptAllocationChart
          data={departmentData}
          title="By department"
          subtitle="Top allocations"
          maxItems={5}
          compact
        />
      ) : (
        <ChartCard
          title="Your department"
          subtitle="Asset allocation"
          data={departmentData}
          emptyHint="No department data."
        >
          <ResponsiveContainer>
            <BarChart data={departmentData} layout="vertical">
              <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" width={88} tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Bar dataKey="count" fill="oklch(0.7 0.16 240)" radius={[0, 6, 6, 0]} maxBarSize={24} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      )}

      <ChartCard
        title="Maintenance activity"
        subtitle="Recent events (not a forecast)"
        data={maintenanceActivity}
        emptyHint="No maintenance events in recent activity."
      >
        <ResponsiveContainer>
          <LineChart data={maintenanceActivity}>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: "rgb(160,160,180)", fontSize: 9 }} axisLine={false} tickLine={false} />
            <YAxis allowDecimals={false} tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={chartTooltipStyle} />
            <Line type="monotone" dataKey="count" stroke="oklch(0.85 0.15 75)" strokeWidth={2} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard
        title="Fleet health estimate"
        subtitle={avgHealthPct != null ? "Based on AI scoring" : "Run scoring for trend"}
        data={healthSpark}
        emptyHint="Run AI scoring on Operations Center."
      >
        <ResponsiveContainer>
          <AreaChart data={healthSpark}>
            <defs>
              <linearGradient id="healthGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="oklch(0.72 0.17 155)" stopOpacity={0.4} />
                <stop offset="100%" stopColor="oklch(0.72 0.17 155)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={chartTooltipStyle} />
            <Area type="monotone" dataKey="value" stroke="oklch(0.72 0.17 155)" fill="url(#healthGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
