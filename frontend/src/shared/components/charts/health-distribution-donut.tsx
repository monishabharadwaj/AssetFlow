import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

type DonutSegment = {
  band: string;
  label: string;
  count: number;
};

type HealthDistributionDonutProps = {
  segments: DonutSegment[];
  total: number;
  centerLabel?: string;
};

const BAND_ORDER = ["EXCELLENT", "HEALTHY", "MONITOR", "WARNING", "CRITICAL"];

const colorMap: Record<string, string> = {
  EXCELLENT: "#10b981",
  HEALTHY: "#22c55e",
  MONITOR: "#fbbf24",
  WARNING: "#f97316",
  CRITICAL: "#ef4444",
};

export function HealthDistributionDonut({
  segments,
  total,
  centerLabel = "Total",
}: HealthDistributionDonutProps) {
  const data = BAND_ORDER.map((band) => {
    const seg = segments.find((s) => s.band === band);
    return { name: seg?.label ?? band, value: seg?.count ?? 0, band };
  }).filter((d) => d.value > 0);

  const chartData = data.length ? data : [{ name: "No data", value: 1, band: "HEALTHY" }];

  return (
    <div className="relative h-52 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={chartData} dataKey="value" innerRadius={62} outerRadius={88} paddingAngle={2} strokeWidth={0}>
            {chartData.map((entry, i) => (
              <Cell key={`cell-${i}`} fill={colorMap[entry.band] ?? "#64748b"} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "hsl(224 24% 11%)",
              border: "1px solid hsl(224 18% 24%)",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-semibold tabular-nums">{total}</span>
        <span className="text-xs text-muted-foreground">{centerLabel}</span>
      </div>
    </div>
  );
}
