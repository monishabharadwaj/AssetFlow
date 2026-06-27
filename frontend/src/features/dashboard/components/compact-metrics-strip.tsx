import { Link } from "react-router-dom";

import type { DashboardSummary } from "../../../shared/api/types";
import { cn } from "../../../shared/lib/utils";

import AssetsIcon from "../../../assets/icons/Assets.png";
import EmployeesIcon from "../../../assets/icons/employees.png";
import DepartmentsIcon from "../../../assets/icons/departments.png";
import MaintenanceIcon from "../../../assets/icons/maintenance.png";

type CompactMetricsStripProps = {
  summary: DashboardSummary;
};

export function CompactMetricsStrip({ summary }: CompactMetricsStripProps) {
  const metrics = [
    {
      label: "Assets",
      value: summary.total_active_assets,
      href: "/assets",
      icon: AssetsIcon,
    },
    {
      label: "Employees",
      value: summary.total_active_employees,
      href: "/employees",
      icon: EmployeesIcon,
    },
    {
      label: "Departments",
      value: summary.total_active_departments,
      href: "/departments",
      icon: DepartmentsIcon,
    },
    {
      label: "Maint. Due",
      value: summary.maintenance_due_count,
      href: "/maintenance",
      icon: MaintenanceIcon,
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {metrics.map((m) => (
        <Link
          key={m.label}
          to={m.href}
          className={cn(
            "group rounded-2xl border border-slate-700 bg-[#111827] px-5 py-4 transition-all duration-300",
            "shadow-[0_0_10px_rgba(59,130,246,0.10)]",
            "hover:-translate-y-1",
            "hover:border-blue-500/60",
            "hover:shadow-[0_0_25px_rgba(59,130,246,0.35)]",
          )}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400">{m.label}</p>

              <p className="mt-2 text-3xl font-bold text-white">
                {m.value.toLocaleString()}
              </p>
            </div>

            <div className="flex h-20 w-20 items-center justify-center rounded-2xl">
              <img
                src={m.icon}
                alt={m.label}
                className="h-24 w-24 object-contain transition-transform duration-300 drop-shadow-[0_0_8px_rgba(96,165,250,0.45)]
             group-hover:scale-110
             group-hover:drop-shadow-[0_0_16px_rgba(96,165,250,0.8)]"
              />
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
