import { useState } from "react";
import { BarChart3, ChevronDown, ChevronUp } from "lucide-react";

import { DepartmentDistributionChart } from "./department-distribution-chart";
import { StatusDistributionChart } from "./status-distribution-chart";
import { Button } from "../../../shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import type { DashboardSummary } from "../../../shared/api/types";
import { cn } from "../../../shared/lib/utils";

type AnalyticsSectionProps = {
  assetsByStatus: DashboardSummary["assets_by_status"];
  assetsByDepartment: DashboardSummary["assets_by_department"];
};

export function AnalyticsSection({ assetsByStatus, assetsByDepartment }: AnalyticsSectionProps) {
  const [open, setOpen] = useState(false);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="h-5 w-5" />
            Analytics
          </CardTitle>
          <CardDescription>Status and department distribution — secondary view</CardDescription>
        </div>
        <Button type="button" variant="ghost" size="sm" onClick={() => setOpen((v) => !v)}>
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
        <div className="grid gap-4 md:grid-cols-2">
          <StatusDistributionChart data={assetsByStatus} />
          <DepartmentDistributionChart data={assetsByDepartment} />
        </div>
      </CardContent>
    </Card>
  );
}
