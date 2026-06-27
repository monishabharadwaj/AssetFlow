import {
  Bar,
  BarChart,
  CartesianGrid,
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

type DepartmentDistributionChartProps = {
  data: Array<{
    department_id: string;
    department_name: string;
    count: number;
  }>;
};

export function DepartmentDistributionChart({
  data,
}: DepartmentDistributionChartProps) {
  const chartData = [...data]
    .sort((a, b) => b.count - a.count)
    .slice(0, 8)
    .map((item) => ({
      name: item.department_name,
      count: item.count,
    }));

  return (
    <Card className="h-full rounded-2xl border border-slate-700 bg-slate-900/50 shadow-[0_0_20px_rgba(59,130,246,0.08)]">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-white">
          Assets by Department
        </CardTitle>
        <CardDescription className="text-slate-400">
          Top departments by active asset count
        </CardDescription>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <EmptyState
            title="No department data yet"
            description="Assign assets to departments to see distribution."
          />
        ) : (
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                layout="vertical"
                margin={{ top: 8, right: 8, left: 8, bottom: 0 }}
              >
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  allowDecimals={false}
                  tick={{ fill: "#CBD5E1", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={100}
                  tick={{ fill: "#CBD5E1", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip formatter={(value) => [value ?? 0, "Assets"]} />
                <Bar dataKey="count" fill="#60A5FA" radius={[0, 10, 10, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
