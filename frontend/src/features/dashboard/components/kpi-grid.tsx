import { Box, Users, Wrench } from "lucide-react";

import type { DashboardSummary } from "../../../shared/api/types";
import { KpiCard } from "./kpi-card";

type KpiGridProps = {
  summary: DashboardSummary;
};

export function KpiGrid({ summary }: KpiGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard
        title="Total Assets"
        value={summary.total_assets}
        subtitle={`${summary.total_active_assets} active`}
        icon={Box}
        href="/assets"
      />
      <KpiCard
        title="Active Assets"
        value={summary.total_active_assets}
        subtitle="Currently in use"
        icon={Box}
        href="/assets?is_active=true"
      />
      <KpiCard
        title="Total Employees"
        value={summary.total_employees}
        subtitle={`${summary.total_active_employees} active`}
        icon={Users}
        href="/employees"
      />
      <KpiCard
        title="Maintenance Due"
        value={summary.maintenance_due_count}
        subtitle="Scheduled or overdue"
        icon={Wrench}
        href="/maintenance"
      />
    </div>
  );
}
