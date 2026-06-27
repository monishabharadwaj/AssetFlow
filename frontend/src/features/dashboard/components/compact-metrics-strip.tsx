import { Link } from "react-router-dom";
import {
  Boxes,
  Users,
  Building2,
  Wrench
} from "lucide-react";

import type { DashboardSummary } from "../../../shared/api/types";
import { cn } from "../../../shared/lib/utils";

type CompactMetricsStripProps = {
  summary: DashboardSummary;
};

export function CompactMetricsStrip({ summary }: CompactMetricsStripProps) {
  const metrics = [
  {
    label: "Assets",
    value: summary.total_active_assets,
    href: "/assets",
    icon: Boxes,
  },
  {
    label: "Employees",
    value: summary.total_active_employees,
    href: "/employees",
    icon: Users,
  },
  {
    label: "Departments",
    value: summary.total_active_departments,
    href: "/departments",
    icon: Building2,
  },
  {
    label: "Maint. Due",
    value: summary.maintenance_due_count,
    href: "/maintenance",
    icon: Wrench,
  },
];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {metrics.map((m) => (
        <Link
          key={m.label}
          to={m.href}
          className={cn(
           "rounded-2xl border border-slate-700 bg-[#111827] px-5 py-4 transition-all duration-300",
           "shadow-[0_0_10px_rgba(59,130,246,0.10)]",
           "hover:border-blue-500/60",
           "hover:shadow-[0_0_25px_rgba(59,130,246,0.35)]",
           "hover:-translate-y-1"
           )}
        >
          <div className="flex items-start justify-between">
          <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">
          {m.label}
          </p>

          <p className="mt-2 text-3xl font-bold text-white">
           {m.value.toLocaleString()}
          </p>
        </div>

       <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 shadow-[0_0_20px_rgba(59,130,246,0.45)]">
       <m.icon className="h-5 w-5 text-white" />
       </div>
       </div>
        </Link>
      ))}
    </div>
  );
}
