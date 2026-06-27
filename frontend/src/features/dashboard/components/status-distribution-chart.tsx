import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { EmptyState } from "../../../shared/components/feedback/empty-state";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import {
  formatStatusLabel,
  getStatusChartColor,
} from "../../../shared/lib/status-colors";

type StatusDistributionChartProps = {
  data: Array<{ status: string; count: number }>;
};

export function StatusDistributionChart({
  data,
}: StatusDistributionChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    label: formatStatusLabel(item.status),
    fill: getStatusChartColor(item.status),
  }));

  return (
    <Card className="h-full rounded-2xl border border-slate-700 bg-slate-900/50 shadow-[0_0_20px_rgba(59,130,246,0.08)]">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-white">
          Asset Status Distribution
        </CardTitle>
        <CardDescription className="text-slate-400">
          Breakdown of active assets by lifecycle status
        </CardDescription>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <EmptyState
            title="No status data yet"
            description="Create assets to see distribution."
          />
        ) : (
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
              >
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                <XAxis
                  dataKey="label"
                  tick={{ fill: "#CBD5E1", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fill: "#CBD5E1", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  formatter={(value) => [value ?? 0, "Assets"]}
                  labelFormatter={(label) => String(label)}
                />
                <Bar dataKey="count" radius={[10, 10, 0, 0]}>
                  {chartData.map((entry) => (
                    <Cell key={entry.status} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
