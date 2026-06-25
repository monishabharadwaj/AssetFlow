import { Link } from "react-router-dom";

import type { DashboardSummary } from "../../../shared/api/types";
import { cn } from "../../../shared/lib/utils";

type CompactMetricsStripProps = {
  summary: DashboardSummary;
};

export function CompactMetricsStrip({ summary }: CompactMetricsStripProps) {
  const metrics = [
    { label: "Assets", value: summary.total_active_assets, href: "/assets" },
    { label: "Employees", value: summary.total_active_employees, href: "/employees" },
    { label: "Departments", value: summary.total_active_departments, href: "/departments" },
    { label: "Maint. Due", value: summary.maintenance_due_count, href: "/maintenance" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {metrics.map((m) => (
        <Link
          key={m.label}
          to={m.href}
          className={cn(
            "rounded-lg border bg-card px-4 py-3 transition-shadow hover:shadow-sm",
          )}
        >
          <p className="text-xs font-medium text-muted-foreground">{m.label}</p>
          <p className="text-xl font-semibold tracking-tight">{m.value.toLocaleString()}</p>
        </Link>
      ))}
    </div>
  );
}
