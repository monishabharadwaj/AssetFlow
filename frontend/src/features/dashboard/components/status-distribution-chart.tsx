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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { formatStatusLabel, getStatusChartColor } from "../../../shared/lib/status-colors";

type StatusDistributionChartProps = {
  data: Array<{ status: string; count: number }>;
};

export function StatusDistributionChart({ data }: StatusDistributionChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    label: formatStatusLabel(item.status),
    fill: getStatusChartColor(item.status),
  }));

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Asset Status Distribution</CardTitle>
        <CardDescription>Breakdown of active assets by lifecycle status</CardDescription>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <EmptyState title="No status data yet" description="Create assets to see distribution." />
        ) : (
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip
                  formatter={(value) => [value ?? 0, "Assets"]}
                  labelFormatter={(label) => String(label)}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
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
