import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ChartPoint } from "../../operations/api/operations-api";

type ReportBarChartProps = {
  data: ChartPoint[];
  valueLabel?: string;
  color?: string;
  height?: number;
};

export function ReportBarChart({
  data,
  valueLabel = "Value",
  color = "#3b82f6",
  height = 220,
}: ReportBarChartProps) {
  if (!data.length) {
    return <p className="text-sm text-muted-foreground">No chart data available.</p>;
  }

  const chartData = data.map((d) => ({ name: d.label, value: d.value }));

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 10 }}
            angle={-25}
            textAnchor="end"
            interval={0}
            height={50}
          />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value) => {
              const num = typeof value === "number" ? value : Number(value ?? 0);
              return [num, valueLabel];
            }}
          />
          <Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
