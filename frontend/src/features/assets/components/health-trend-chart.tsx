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

export function HealthTrendChart({ items, predictedScore }: HealthTrendChartProps) {
  const sorted = [...items]
    .filter((h) => h.health_score != null)
    .sort((a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime());

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
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
          <Tooltip formatter={(value) => [`${Number(value ?? 0)}%`, "Health"]} />
          <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
          {predictedScore != null ? (
            <ReferenceDot
              x={last?.date}
              y={Math.round(predictedScore * 100)}
              r={5}
              fill="hsl(var(--destructive))"
              stroke="none"
            />
          ) : null}
        </LineChart>
      </ResponsiveContainer>
      {predictedScore != null ? (
        <p className="mt-1 text-xs text-muted-foreground">
          Red dot: latest AI prediction ({Math.round(predictedScore * 100)}%)
        </p>
      ) : null}
    </div>
  );
}
