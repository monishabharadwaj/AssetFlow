import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { Card, CardHeader, EmptyState } from "@/components/ui-bits";
import { chartTooltipStyle, RISK_COLORS } from "@/lib/chart-theme";

type Bands = { healthy: number; monitor: number; warning: number; critical: number };

const BAND_META = [
  { key: "critical" as const, label: "Critical", color: RISK_COLORS.critical },
  { key: "warning" as const, label: "Warning", color: RISK_COLORS.warning },
  { key: "monitor" as const, label: "Monitor", color: RISK_COLORS.monitor },
  { key: "healthy" as const, label: "Healthy", color: RISK_COLORS.healthy },
];

export function RiskBandChart({
  bands,
  title = "Fleet health bands",
  subtitle = "AI risk distribution",
}: {
  bands: Bands;
  title?: string;
  subtitle?: string;
}) {
  const data = BAND_META.map((b) => ({ name: b.label, value: bands[b.key], color: b.color })).filter((d) => d.value > 0);
  const total = data.reduce((a, b) => a + b.value, 0);

  return (
    <Card className="h-full">
      <CardHeader title={title} subtitle={subtitle} />
      {total === 0 ? (
        <EmptyState title="No health data" hint="Run analysis to populate health bands." />
      ) : (
        <div className="flex items-center gap-4">
          <div className="relative size-36 shrink-0">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={data} dataKey="value" innerRadius={42} outerRadius={62} paddingAngle={3} stroke="none">
                  {data.map((d) => <Cell key={d.name} fill={d.color} />)}
                </Pie>
                <Tooltip contentStyle={chartTooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 grid place-items-center pointer-events-none">
              <span className="text-xl font-semibold tabular-nums">{total}</span>
            </div>
          </div>
          <div className="flex-1 space-y-2 text-sm">
            {BAND_META.map((b) => (
              <div key={b.key} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="size-2.5 rounded-full" style={{ background: b.color }} />
                  <span className="text-muted-foreground">{b.label}</span>
                </div>
                <span className="tabular-nums font-medium">{bands[b.key]}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
