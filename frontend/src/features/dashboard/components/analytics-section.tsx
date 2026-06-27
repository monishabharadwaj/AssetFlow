import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import analyticsIcon from "../../../assets/icons/analytics.png";

import { DepartmentDistributionChart } from "./department-distribution-chart";
import { StatusDistributionChart } from "./status-distribution-chart";
import { Button } from "../../../shared/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import type { DashboardSummary } from "../../../shared/api/types";
import { cn } from "../../../shared/lib/utils";

type AnalyticsSectionProps = {
  assetsByStatus: DashboardSummary["assets_by_status"];
  assetsByDepartment: DashboardSummary["assets_by_department"];
};

export function AnalyticsSection({
  assetsByStatus,
  assetsByDepartment,
}: AnalyticsSectionProps) {
  const [open, setOpen] = useState(false);

  return (
    <Card className="rounded-2xl border border-slate-700 bg-[#111827] shadow-[0_0_25px_rgba(59,130,246,0.08)]">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="flex items-center gap-3 text-xl font-semibold text-white">
            <img
              src={analyticsIcon}
              alt="Analytics"
              className="h-14 w-14 object-contain
             transition-all duration-300
             drop-shadow-[0_0_12px_rgba(6,182,212,0.45)]
             hover:scale-105
             hover:drop-shadow-[0_0_20px_rgba(6,182,212,0.75)]"
            />
            Analytics
          </CardTitle>
          <CardDescription className="text-slate-400">
            Live overview of asset distribution
          </CardDescription>
        </div>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="border-blue-500/30 bg-slate-900 text-blue-300 transition-all hover:border-blue-400 hover:bg-blue-500/10 hover:shadow-[0_0_18px_rgba(59,130,246,0.35)]"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? (
            <>
              Hide <ChevronUp className="ml-1 h-4 w-4" />
            </>
          ) : (
            <>
              Show <ChevronDown className="ml-1 h-4 w-4" />
            </>
          )}
        </Button>
      </CardHeader>
      <CardContent className={cn(!open && "hidden")}>
        <div className="grid gap-6 md:grid-cols-2">
          <StatusDistributionChart data={assetsByStatus} />
          <DepartmentDistributionChart data={assetsByDepartment} />
        </div>
      </CardContent>
    </Card>
  );
}
