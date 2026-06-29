import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardHeader, EmptyState } from "@/components/ui-bits";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { chartTooltipStyle } from "@/lib/chart-theme";
import { cn } from "@/lib/utils";

export function DeptAllocationChart({
  data,
  title,
  subtitle,
  maxItems = 6,
  compact = false,
}: {
  data: { name: string; count: number }[];
  title: string;
  subtitle: string;
  maxItems?: number;
  compact?: boolean;
}) {
  const chartData = [...data].sort((a, b) => b.count - a.count).slice(0, maxItems);
  const height = compact ? "h-48" : "h-52";

  return (
    <Card className={cn(glassCardClass(), "h-full")}>
      <CardHeader title={title} subtitle={subtitle} />
      <div className={height}>
        {chartData.length === 0 ? (
          <EmptyState title="No data" />
        ) : (
          <ResponsiveContainer>
            <BarChart data={chartData} layout="vertical" margin={{ left: 4, right: 8 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis
                type="category"
                dataKey="name"
                width={compact ? 88 : 100}
                tick={{ fill: "rgb(160,160,180)", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
              <Bar dataKey="count" fill="oklch(0.7 0.16 240)" radius={[0, 6, 6, 0]} maxBarSize={28} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </Card>
  );
}
