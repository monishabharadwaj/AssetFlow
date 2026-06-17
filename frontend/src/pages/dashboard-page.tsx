import { ActivityFeed } from "../features/dashboard/components/activity-feed";
import { DashboardError } from "../features/dashboard/components/dashboard-error";
import { DashboardSkeleton } from "../features/dashboard/components/dashboard-skeleton";
import { DepartmentDistributionChart } from "../features/dashboard/components/department-distribution-chart";
import { KpiGrid } from "../features/dashboard/components/kpi-grid";
import { QuickActionsPanel } from "../features/dashboard/components/quick-actions-panel";
import { StatusDistributionChart } from "../features/dashboard/components/status-distribution-chart";
import { useDashboardSummary } from "../features/dashboard/hooks/use-dashboard-summary";

export function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useDashboardSummary();

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (isError || !data) {
    return (
      <div className="grid gap-4 md:gap-6">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Dashboard</h2>
          <p className="text-sm text-muted-foreground">Asset lifecycle overview and recent activity</p>
        </div>
        <DashboardError
          message={error instanceof Error ? error.message : undefined}
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:gap-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Dashboard</h2>
        <p className="text-sm text-muted-foreground">Asset lifecycle overview and recent activity</p>
      </div>

      <KpiGrid summary={data} />

      <div className="grid gap-4 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <StatusDistributionChart data={data.assets_by_status} />
        </div>
        <div className="lg:col-span-4">
          <DepartmentDistributionChart data={data.assets_by_department} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <ActivityFeed activities={data.recent_activity} />
        </div>
        <div className="lg:col-span-4">
          <QuickActionsPanel />
        </div>
      </div>
    </div>
  );
}
