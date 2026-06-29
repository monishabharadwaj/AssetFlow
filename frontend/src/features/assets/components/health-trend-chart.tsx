import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { HealthHistory } from "../../../shared/api/types";
import { formatDate } from "../../../shared/lib/format";

type HealthTrendChartProps = {
  items: HealthHistory[];
  predictedScore?: number | null;
};

export function HealthTrendChart({
  items,
  predictedScore,
}: HealthTrendChartProps) {
  const sorted = [...items]
    .filter((h) => h.health_score != null)
    .sort(
      (a, b) =>
        new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime(),
    );

  if (sorted.length < 2) {
    return (
      <p className="text-sm text-muted-foreground">
        At least two health snapshots are needed to show a trend.
      </p>
    );
  }

  const data = sorted.map((h) => ({
    date: formatDate(h.recorded_at),
    score: Math.round(Number(h.health_score) * 100),
  }));

  const last = data[data.length - 1];

  return (
    <div className="h-64 w-full rounded-2xl border border-slate-700 bg-[#111827] p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
        >
          <CartesianGrid stroke="#334155" strokeDasharray="4 4" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#94A3B8" }}
            axisLine={{ stroke: "#475569" }}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            unit="%"
            tick={{ fontSize: 11, fill: "#94A3B8" }}
            axisLine={{ stroke: "#475569" }}
            tickLine={false}
          />
          <Tooltip
            formatter={(value) => [`${Number(value ?? 0)}%`, "Health"]}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#3B82F6"
            strokeWidth={3}
            dot={false}
          />
          {predictedScore != null ? (
            <ReferenceDot
              x={last?.date}
              y={Math.round(predictedScore * 100)}
              r={5}
              fill="#EF4444"
              stroke="none"
            />
          ) : null}
        </LineChart>
      </ResponsiveContainer>
      {predictedScore != null ? (
        <p className="mt-1 text-xs text-slate-400">
          Red dot: latest AI prediction ({Math.round(predictedScore * 100)}%)
        </p>
      ) : null}
    </div>
  );
}
